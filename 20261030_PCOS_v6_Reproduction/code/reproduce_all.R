#!/usr/bin/env Rscript
# 独立 base R 复现：原始数据 -> 全部核心/敏感性 CSV -> 12 张 R 图。
# 不调用 Python，不把既有结果作为估计输入；旧结果仅用于算完后的核对。
arg <- grep('^--file=',commandArgs(),value=TRUE)
arg <- gsub('~+~',' ',arg,fixed=TRUE) # Rscript encodes spaces in --file on some platforms.
root <- if(length(arg)) dirname(dirname(normalizePath(sub('^--file=','',arg[1]),winslash='/'))) else getwd()
if(!file.exists(file.path(root,'docs','20261030_INPUT_CHECKSUMS.csv'))) stop('Set working directory to the package root.')
options(encoding='UTF-8')
input_manifest <- read.csv(file.path(root,'docs','20261030_INPUT_CHECKSUMS.csv'),stringsAsFactors=FALSE)
for(i in seq_len(nrow(input_manifest))) {
 p<-file.path(root,input_manifest$path[i]);stopifnot(file.exists(p),file.info(p)$size==input_manifest$bytes[i],unname(tools::md5sum(p))==input_manifest$md5[i])
}
# Original core executes here, using only raw inputs and independent base-R arithmetic.
source(file.path(root,'code','PCOS_NewArticle_complete.R'),encoding='UTF-8')
cells<-pcos_results$rate_cells;out<-file.path(root,'results','R')
read_input<-function(n)read.csv(file.path(root,'data','input',n),stringsAsFactors=FALSE,fileEncoding='UTF-8',check.names=FALSE)
write_out<-function(x,n)write.csv(x,file.path(out,paste0(n,'.csv')),row.names=FALSE,na='',fileEncoding='UTF-8')
ages<-seq(15,45,5);years<-1990:2023;types<-c('Total','Primary','Secondary');causes<-c('Polycystic ovarian syndrome','Endometriosis')
refs<-sort(setdiff(unique(cells$country),'China'));raww<-read_input('weights.csv')$weight;w<-raww/sum(raww)
grid<-expand.grid(country=refs,age_start=ages,year=years,stringsAsFactors=FALSE)
key<-function(x)paste(x$country,x$age_start,x$year,sep='__')
pop<-cells[!duplicated(cells[c('country','age_start','year')]),];pm<-pop[match(key(grid),key(pop)),];stopifnot(!anyNA(pm))
shares<-list()
for(src in c('GBD','UN-WPP2024')){
 p<-array(pm[[if(src=='GBD')'gbd_pop' else 'un_female_pop']],c(18,7,34));shares[[src]]<-sweep(p,c(2,3),apply(p,c(2,3),sum),'/')
}
sens<-list();age_rows<-list();roundrows<-list()
corner_signs<-as.matrix(expand.grid(rep(list(c(-1,1)),7)))
corners<-sweep(corner_signs*.5e-6,2,raww,'+');corners<-corners/rowSums(corners)
for(cause in causes)for(subtype in types){
 z<-cells[cells$cause==cause & cells$subtype==subtype,]
 rr<-array(z$gbd_rate[match(key(grid),key(z))],c(18,7,34));cg<-expand.grid(age_start=ages,year=years);cz<-z[z$country=='China',]
 cc<-matrix(cz$gbd_rate[match(paste(cg$age_start,cg$year),paste(cz$age_start,cz$year))],nrow=7)
 stopifnot(all(is.finite(rr)),all(is.finite(cc)))
 for(src in names(shares)){
  s<-shares[[src]];scenarios<-list(main=list(s=s,w=w),ages20_49=list(s=s,w=c(0,w[-1]/sum(w[-1]))))
  for(k in seq_along(refs)){ss<-s;ss[k,,]<-0;ss<-sweep(ss,c(2,3),apply(ss,c(2,3),sum),'/');scenarios[[paste0('omit_',refs[k])]]<-list(s=ss,w=w)}
  for(scenario in names(scenarios))for(start in c(1990,2010))for(end in c(2021,2022,2023)){
   ss<-scenarios[[scenario]]$s;ww<-scenarios[[scenario]]$w;i<-match(start,years);j<-match(end,years)
   r0<-rr[,,i];r1<-rr[,,j];s0<-ss[,,i];s1<-ss[,,j]
   xage<-ww*(cc[,j]-cc[,i]);qage<--ww*colSums((s0+s1)/2*(r1-r0));sage<--ww*colSums((r0+r1)/2*(s1-s0))
   initial<-sum(ww*(cc[,i]-colSums(s0*r0)));last<-sum(ww*(cc[,j]-colSums(s1*r1)));net<-last-initial
   x<-sum(xage);q<-sum(qage);sc<-sum(sage);res<-x+q+sc-net;stopifnot(abs(res)<1e-8)
   sens[[length(sens)+1]]<-data.frame(cause=cause,subtype=subtype,source=src,scenario=scenario,start=start,end=end,initial_gap=initial,end_gap=last,net_gap_change=net,china_rate_effect=x,reference_rate_effect=q,reference_country_composition_effect=sc,composition_share_of_net=if(abs(net)>1e-10)sc/net else NA_real_,identity_residual=res)
   if(scenario=='main' && start==1990)age_rows[[length(age_rows)+1]]<-data.frame(cause=cause,subtype=subtype,source=src,start=start,end=end,age_start=ages,china_rate_effect=xage,reference_rate_effect=qage,reference_country_composition_effect=sage,net_gap_change=xage+qage+sage)
  }
  g<-cc[,34]-colSums(s[,,34]*rr[,,34]);netage<-g-(cc[,1]-colSums(s[,,1]*rr[,,1]));sage<--colSums((rr[,,1]+rr[,,34])/2*(s[,,34]-s[,,1]))
  gaps<-as.vector(corners%*%g);sc<-as.vector(corners%*%sage);net<-as.vector(corners%*%netage)
  roundrows[[length(roundrows)+1]]<-data.frame(cause=cause,subtype=subtype,source=src,gap_min=min(gaps),gap_max=max(gaps),share_effect_min=min(sc),share_effect_max=max(sc),fraction_min=min(sc/net),fraction_max=max(sc/net))
 }
}
sens<-do.call(rbind,sens);age_rows<-do.call(rbind,age_rows);rounding<-do.call(rbind,roundrows)
stopifnot(nrow(sens)==1440,max(abs(sens$identity_residual))<1e-8)
write_out(sens,'composition_sensitivities');write_out(age_rows,'age_decomposition');write_out(rounding,'standard_weight_rounding')
national<-cells; national$aspr<-national$gbd_rate*w[match(national$age_start,ages)];national$cases<-national$gbd_cases
national<-aggregate(cbind(aspr,cases)~country+cause+subtype+year,national,sum)
national<-national[do.call(order,national[c('country','cause','subtype','year')]),]
national$yoy_percent<-ave(national$aspr,interaction(national$country,national$cause,national$subtype,drop=TRUE),FUN=function(x)c(NA_real_,(x[-1]/x[-length(x)]-1)*100))
write_out(national,'national_annual_standardized')
hist<-aggregate(yoy_percent~country+cause+subtype,national[national$year>=1991 & national$year<=2022,],max);names(hist)[4]<-'historical_max_yoy'
terminal<-merge(national[national$year==2023,],hist,by=c('country','cause','subtype'));write_out(terminal,'terminal_year_audit')
ec<-cells[cells$country=='China' & cells$cause=='Endometriosis' & cells$subtype!='Total' & cells$year %in% c(2022,2023),]
ec<-reshape(ec[c('age_start','subtype','year','gbd_rate')],idvar=c('age_start','subtype'),timevar='year',direction='wide');names(ec)<-sub('gbd_rate.','',names(ec),fixed=TRUE)
ec$weighted_increment<-(ec[['2023']]-ec[['2022']])*w[match(ec$age_start,ages)];write_out(ec,'endometriosis_terminal_age_type')
shifts<-list()
for(src in names(shares))for(k in seq_along(refs)){s<-shares[[src]];shifts[[length(shifts)+1]]<-data.frame(source=src,country=refs[k],share1990=sum(s[k,,1]*w),share2023=sum(s[k,,34]*w),share_change=sum((s[k,,34]-s[k,,1])*w))}
shifts<-do.call(rbind,shifts);write_out(shifts,'age_weighted_reference_shifts')
tvd<-apply(abs(shares$GBD-shares[['UN-WPP2024']]),c(2,3),sum)/2
tg<-expand.grid(age_start=ages,year=years);tg$total_variation_distance<-as.vector(tvd);write_out(tg,'population_share_TVD')
annual<-pcos_results$all_annual_benchmark_aspr
wide<-reshape(annual[c('cause','source','benchmark','year','subtype','gap')],idvar=c('cause','source','benchmark','year'),timevar='subtype',direction='wide');names(wide)<-sub('gap.','',names(wide),fixed=TRUE)
wide$sum_residual<-wide$Total-wide$Primary-wide$Secondary;stopifnot(nrow(wide)==408,max(abs(wide$sum_residual))<1e-8)
write_out(wide,'v6_annual_subtype_differences')
# Independent R-only regression checks: never use the archived estimates as inputs.
keysets<-list(all_annual_benchmark_aspr=c('cause','subtype','source','year','benchmark'),symmetric_decomposition_1990_endpoints=c('cause','subtype','source','end'),leave_one_country_out=c('cause','subtype','source','omitted_country'),annual_chained_decomposition=c('cause','subtype','source'),composition_sensitivities=c('cause','subtype','source','scenario','start','end'),age_decomposition=c('cause','subtype','source','start','end','age_start'),national_annual_standardized=c('country','cause','subtype','year'),terminal_year_audit=c('country','cause','subtype','year'),endometriosis_terminal_age_type=c('age_start','subtype'),age_weighted_reference_shifts=c('source','country'),population_share_TVD=c('age_start','year'),standard_weight_rounding=c('cause','subtype','source'))
audit<-list()
for(n in names(keysets)){
 got<-read.csv(file.path(out,paste0(n,'.csv')),stringsAsFactors=FALSE,fileEncoding='UTF-8',check.names=FALSE)
 expected<-read.csv(file.path(root,'reference','aggregates',paste0(n,'.csv')),stringsAsFactors=FALSE,fileEncoding='UTF-8',check.names=FALSE)
 ks<-keysets[[n]];mk<-function(x)do.call(paste,c(x[ks],sep='__'));stopifnot(!anyDuplicated(got[ks]),!anyDuplicated(expected[ks]),nrow(got)==nrow(expected),setequal(mk(got),mk(expected)),setequal(names(got),names(expected)))
 got<-got[match(mk(expected),mk(got)),];nums<-setdiff(names(expected)[vapply(expected,is.numeric,logical(1))],ks)
 xx<-as.matrix(expected[nums]);yy<-as.matrix(got[nums]);stopifnot(all(is.na(xx)==is.na(yy)));delta<-max(abs(xx-yy),na.rm=TRUE);stopifnot(delta<1e-8)
 audit[[length(audit)+1]]<-data.frame(table=n,rows=nrow(got),max_absolute_difference=delta,status='passed')
}
dir.create(file.path(root,'verification'),showWarnings=FALSE)
write.csv(do.call(rbind,audit),file.path(root,'verification','20261030_R_INDEPENDENT_CHECK.csv'),row.names=FALSE)
source(file.path(root,'code','figures_R.R'),encoding='UTF-8')
make_paper_figures_R(root)
cat('Base R: complete core + 1440 sensitivity rows + all twelve paper figures completed.\n')
