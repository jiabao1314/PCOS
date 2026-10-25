# Independent survey-package reconstruction from original CDC public-use records.
suppressPackageStartupMessages(library(survey))
args <- commandArgs(trailingOnly=TRUE)
infile <- if(length(args)>=1) args[1] else 'data/external/nsfg/NSFG_2022_2023_FemRespPUFData.csv'
outdir <- if(length(args)>=2) args[2] else 'results/external/Rcheck'
dir.create(outdir,recursive=TRUE,showWarnings=FALSE)
d <- read.csv(infile,check.names=FALSE)
stopifnot(nrow(d)==5586, all(d$WGT2022_2023>0))
base <- data.frame(VEST=d$VEST, VECL=d$VECL, WGT=d$WGT2022_2023)
ids <- c(); nums <- c(); dens <- c()
broad <- (d$FECUND %in% c(3,4,5)) | (d$INFERT %in% 2)
narrow <- d$INFERT %in% 2
union <- d$RMARITAL %in% c(1,2)
sy <- (d$HLPPRG %in% 1)|(d$HLPMC %in% 1)
sk <- sy|((d$HLPPRG %in% 5)&(d$HLPMC %in% 5))
add <- function(id,num,den) {
 k <- length(ids)+1
 ids <<- c(ids,id); nums <<- c(nums,paste0('num',k));dens <<- c(dens,paste0('den',k))
 base[[paste0('num',k)]] <<- as.numeric(num)
 base[[paste0('den',k)]] <<- as.numeric(den)
}
for(scope in c('strict_20_49','sampled_20plus')) {
 eligible <- d$AGER>=20 & d$AGER<=ifelse(scope=='strict_20_49',49,50)
 for(dis in c('ENDO','PCOS')) {
  valid <- d[[dis]] %in% c(1,5); diagnosed <- d[[dis]] %in% 1
  add(paste(scope,dis,'diagnosis',sep='_'),eligible&valid&diagnosed,eligible&valid)
  outcomes <- list(current_problems_all=list(broad,eligible),current_problems_union=list(broad,eligible&union),infertility12_union=list(narrow,eligible&union&(d$INFERT %in% c(1,2,3))),ever_services_all=list(sy,eligible&sk))
  for(out in names(outcomes)) {
   for(group in c('diagnosed','not_diagnosed')) {
    mask <- outcomes[[out]][[2]] & valid & (diagnosed==(group=='diagnosed'))
    add(paste(scope,dis,out,group,sep='_'),mask&outcomes[[out]][[1]],mask)
   }
  }
 }
}
design <- svydesign(ids=~VECL,strata=~VEST,weights=~WGT,nest=TRUE,data=base)
ind <- lapply(seq_along(ids),function(k) {
 a <- svyratio(as.formula(paste0('~',nums[k])),as.formula(paste0('~',dens[k])),design)
 data.frame(estimate_id=ids[k],p=unname(coef(a)[1]),se=unname(SE(a)[1]),df=degf(design))
})
est <- do.call(rbind,ind)
tot <- svytotal(as.formula(paste('~',paste(c(nums,dens),collapse='+'))),design)
z <- coef(tot);J <- matrix(0,nrow=length(ids),ncol=length(z))
for(k in seq_along(ids)) {
 a <- match(nums[k],names(z)); b <- match(dens[k],names(z))
 J[k,a] <- 1/z[b];J[k,b] <- -z[a]/z[b]^2
}
V <- J%*%vcov(tot)%*%t(J);rownames(V)<-ids;colnames(V)<-ids
stopifnot(max(abs(sqrt(diag(V))-est$se))<1e-10)
write.csv(est,file.path(outdir,'independent_R_estimates.csv'),row.names=FALSE)
write.csv(V,file.path(outdir,'independent_R_joint_covariance.csv'))
writeLines(capture.output(sessionInfo()),file.path(outdir,'R_session_info.txt'))
cat('Independent reconstruction:',nrow(est),'estimates; df=',degf(design),'\n')
print(est)
