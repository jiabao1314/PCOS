# Independent validation of Python Taylor calculations using R package survey.
# Public respondent data are read locally and never written to public outputs.
suppressPackageStartupMessages(library(survey))
d<-read.csv('data/raw/nsfg_2022_2023/NSFG_2022_2023_FemRespPUFData.csv')
d$problem<-as.numeric(d$FECUND %in% c(3,4,5) | d$INFERT %in% 2)
d$eligible<-d$AGER>=20 & d$AGER<=49
d$age5<-paste0(5*(d$AGER%/%5),'-',5*(d$AGER%/%5)+4)
w<-read.csv('data/processed/weights.csv');w<-w[w$age_name!='15-19',];w$weight<-w$weight/sum(w$weight)
out<-list()
for(causevar in c('ENDO','PCOS')) {
 cause<-ifelse(causevar=='ENDO','Endometriosis','Polycystic ovarian syndrome')
 valid<-d$eligible & d[[causevar]] %in% c(1,5)
 diagnosed<-as.numeric(d[[causevar]] %in% 1)
 joint<-diagnosed*d$problem
 sets<-list(ever_diagnosed=list(y=diagnosed,domain=valid),current_problem_if_diagnosed=list(y=d$problem,domain=valid & diagnosed==1),current_problem_if_not_diagnosed=list(y=d$problem,domain=valid & diagnosed==0),cooccurring_diagnosis_and_problem=list(y=joint,domain=valid),cooccurrence_no_prior_live_birth=list(y=joint*(d$PARITY==0),domain=valid),cooccurrence_at_least_one_live_birth=list(y=joint*(d$PARITY>0),domain=valid))
 for(metric in names(sets)) {
  d$y<-sets[[metric]]$y;d$domain<-sets[[metric]]$domain
  des<-svydesign(ids=~VECL,strata=~VEST,weights=~WGT2022_2023,nest=TRUE,data=d)
  q<-svymean(~y,subset(des,domain));
  out[[length(out)+1]]<-data.frame(cause=cause,metric=metric,standard='survey_weighted_crude',r_percent=100*as.numeric(coef(q)),r_se_percent=100*as.numeric(SE(q)))
  if(!grepl('^current_problem_if_',metric)) {
   by<-svyby(~y,~age5,subset(des,domain),svymean,covmat=TRUE)
   wt<-w$weight[match(as.character(by$age5),w$age_name)]
   p<-sum(wt*coef(by));v<-drop(t(wt)%*%vcov(by)%*%wt)
   out[[length(out)+1]]<-data.frame(cause=cause,metric=metric,standard='GBD_weights_20_49',r_percent=100*p,r_se_percent=100*sqrt(v))
  }
 }
}
r<-do.call(rbind,out);p<-read.csv('results/tables/nsfg_external_estimates.csv')
q<-merge(p,r,by=c('cause','metric','standard'))
stopifnot(nrow(q)==20)
q$absolute_point_difference<-abs(q$estimate_percent-q$r_percent);q$absolute_se_difference<-abs(q$se_percent-q$r_se_percent)
stopifnot(max(q$absolute_point_difference)<1e-10,max(q$absolute_se_difference)<1e-10)
write.csv(q[,c('cause','metric','standard','r_percent','r_se_percent','absolute_point_difference','absolute_se_difference')],'results/tables/nsfg_R_crosscheck.csv',row.names=FALSE)
capture.output(sessionInfo(),file='docs/R_survey_session_info.txt')
cat('R/survey agreement for all 20 point estimates and Taylor SEs; maximum SE discrepancy:',max(q$absolute_se_difference),'percentage points\n')
# Definition-sensitive comparisons use a different partnership domain.
sens<-list()
for(causevar in c('ENDO','PCOS')) {
 cause<-ifelse(causevar=='ENDO','Endometriosis','Polycystic ovarian syndrome')
 for(state in c(1,5)) {
  d$y<-as.numeric(d$INFERT %in% 2);d$domain<-d$eligible & d[[causevar]] %in% state & d$RMARITAL %in% c(1,2)
  des<-svydesign(ids=~VECL,strata=~VEST,weights=~WGT2022_2023,nest=TRUE,data=d)
  v<-svymean(~y,subset(des,domain))
  sens[[length(sens)+1]]<-data.frame(cause=cause,metric=paste0('12month_infertility_in_union_',ifelse(state==1,'diagnosed','not_diagnosed')),r_percent=100*as.numeric(coef(v)),r_se_percent=100*as.numeric(SE(v)))
 }
}
sens<-do.call(rbind,sens);py<-read.csv('results/tables/nsfg_definition_missingness_sensitivity.csv')
x<-merge(sens,py,by=c('cause','metric'));stopifnot(nrow(x)==4, max(abs(x$r_percent-x$estimate_percent))<1e-10,max(abs(x$r_se_percent-x$se_percent))<1e-10)
write.csv(x[,c('cause','metric','r_percent','r_se_percent')],'results/tables/nsfg_R_definition_crosscheck.csv',row.names=FALSE)
cat('Four additional narrower-definition estimates and SEs independently matched.\n')
