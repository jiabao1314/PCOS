# Each figure reads independent R outputs. Base-R style differs from Matplotlib;
# scientific values, selections, axes and signs correspond to the same paper.
make_paper_figures_R<-function(root){
 read<-function(n)read.csv(file.path(root,'results','R',paste0(n,'.csv')),stringsAsFactors=FALSE,fileEncoding='UTF-8',check.names=FALSE)
 a<-read('all_annual_benchmark_aspr');d<-read('symmetric_decomposition_1990_endpoints');sens<-read('composition_sensitivities');shifts<-read('age_weighted_reference_shifts');terminal<-read('terminal_year_audit');ec<-read('endometriosis_terminal_age_type')
 pcos<-'Polycystic ovarian syndrome';cols<-c('#19566c','#ba572a','#6b8990');types<-c('Total','Primary','Secondary')
 out<-file.path(root,'figures','R');dir.create(out,recursive=TRUE,showWarnings=FALSE)
 line2<-function(z,x='year',y1='china_aspr',y2='ref_aspr',main='',ylab='Per 100,000'){
  z<-z[order(z[[x]]),];lim<-range(c(z[[y1]],z[[y2]]));lim[2]<-lim[2]+.20*diff(lim);plot(z[[x]],z[[y1]],type='l',col=cols[1],lwd=2,xlab='Year',ylab=ylab,main=main,ylim=lim);lines(z[[x]],z[[y2]],col=cols[2],lwd=2);legend('topleft',c('China','18-country reference'),col=cols[1:2],lty=1,bty='o',bg='white',box.col='white',inset=.02,cex=.8)
 }
 draw<-function(id){
  par(mar=c(4.5,5,3,1),las=1,cex=.9)
  dyn<-a[a$source=='GBD' & a$benchmark=='dynamic',]
  if(id==1){par(mfrow=c(1,2));z<-dyn[dyn$cause==pcos & dyn$subtype=='Total',];line2(z,main='A PCOS total infertility');plot(z$year,z$gap,type='l',lwd=2,col=cols[1],xlab='Year',ylab='China minus reference / 100,000',main='B Rate difference');abline(h=0,col='gray60')}
  if(id==2){par(mfrow=c(1,2));for(t in types[2:3])line2(dyn[dyn$cause==pcos & dyn$subtype==t,],main=paste(t,'infertility'))}
  if(id==3){z<-d[d$cause==pcos & d$source=='GBD' & d$end==2023,];z<-z[match(types,z$subtype),];m<-t(as.matrix(z[c('china_rate_effect','reference_rate_effect','reference_country_composition_effect')]));x<-barplot(m,beside=TRUE,col=cols,names.arg=types,ylim=c(-270,340),ylab='Contribution / 100,000');points(colMeans(x),z$net_gap_change,pch=18);abline(h=0,col='gray50');legend('topright',c('China rates X','Reference rates Q','Reference shares S','Net change'),fill=c(cols,NA),pch=c(NA,NA,NA,18),bty='o',bg='white',box.col='white',inset=.02,cex=.8)}
  if(id==4){par(mfrow=c(1,2));z<-a[a$cause==pcos & a$subtype=='Total' & a$benchmark=='dynamic',];gbd<-z[z$source=='GBD',];un<-z[z$source=='UN-WPP2024',];plot(gbd$year,gbd$gap,type='l',col=cols[1],lwd=2,ylim=range(z$gap),xlab='Year',ylab='China minus reference / 100,000',main='A Population source');lines(un$year,un$gap,col=cols[2],lty=2,lwd=2);legend('topleft',c('GBD','UN WPP2024'),col=cols[1:2],lty=c(1,2),bty='o',bg='white',box.col='white',inset=.02,cex=.8);v<-d[d$cause==pcos & d$subtype=='Total' & d$end==2023,];v<-v[match(c('GBD','UN-WPP2024'),v$source),];barplot(as.matrix(v[c('china_rate_effect','reference_rate_effect','reference_country_composition_effect')]),beside=TRUE,col=cols[1:2],names.arg=c('China X','Reference Q','Shares S'),ylab='Contribution / 100,000',main='B Decomposition');abline(h=0,col='gray50')}
  if(id==5){par(mar=c(5,13,2,2));z<-a[a$cause==pcos & a$subtype=='Secondary' & a$year==2023,];b<-c('dynamic','fixed1990','equal');m<-rbind(z$gap[match(paste('GBD',b),paste(z$source,z$benchmark))],z$gap[match(paste('UN-WPP2024',b),paste(z$source,z$benchmark))]);barplot(m,beside=TRUE,horiz=TRUE,col=cols[1:2],names.arg=c('Current-year shares','Fixed-1990 shares','Equal countries'),xlim=c(-155,40),xlab='China minus reference / 100,000');abline(v=0,col='gray50');legend('topright',c('GBD','UN WPP2024'),fill=cols[1:2],bty='o',bg='white',box.col='white',inset=.02)}
  ss<-sens[sens$cause==pcos & sens$subtype=='Total' & sens$start==1990 & sens$end==2023 & sens$source=='GBD',];labs<-sub('omit_','Without ',ss$scenario,fixed=TRUE);labs[labs=='main']<-'Main';labs[labs=='ages20_49']<-'Ages 20-49'
  if(id %in% c(6,8)){par(mar=c(5,15,2,2));v<-if(id==6)ss$end_gap else ss$composition_share_of_net*100;barplot(rev(v),names.arg=rev(labs),horiz=TRUE,col=if(id==6)cols[1] else cols[3],cex.names=.75,xlab=if(id==6)'2023 PCOS difference / 100,000' else '100 x S / signed net change (%)');abline(v=if(id==6)0 else 50,lty=if(id==6)1 else 2,col='gray50')}
  if(id==7){par(mfrow=c(1,2));for(t in types[2:3]){z<-a[a$cause==pcos & a$subtype==t & a$source=='UN-WPP2024',];b<-c('dynamic','fixed1990','equal');plot(NA,xlim=range(z$year),ylim=range(z$gap),xlab='Year',ylab='Difference / 100,000',main=t);for(j in 1:3){v<-z[z$benchmark==b[j],];lines(v$year,v$gap,col=cols[j],lwd=2)};abline(h=0,col='gray60');legend('topleft',c('Current-year','Fixed 1990','Equal countries'),col=cols,lty=1,bty='o',bg='white',box.col='white',inset=.02,cex=.75)}}
  if(id==9){z<-dyn[dyn$cause=='Endometriosis' & dyn$subtype=='Total',];plot(z$year,z$gap,type='l',lwd=2,col=cols[1],xlab='Year',ylab='China minus reference / 100,000');abline(h=0,col='gray60');p<-z[z$year %in% c(2021,2022,2023),];points(p$year,p$gap,col=cols[2],pch=16)}
  if(id==10){par(mar=c(5,13,2,2));z<-shifts[shifts$source=='UN-WPP2024',];z<-z[order(z$share_change),];barplot(z$share_change*100,horiz=TRUE,names.arg=z$country,col=cols[1],cex.names=.75,xlab='Age-weighted reference share change (percentage points)');abline(v=0,col='gray60')}
  if(id==11){par(mar=c(5,13,2,2));z<-terminal[terminal$cause=='Endometriosis' & terminal$subtype=='Total',];z<-z[order(z$yoy_percent),];barplot(z$yoy_percent,horiz=TRUE,names.arg=z$country,col=cols[2],cex.names=.75,xlab='2022-2023 modeled rate change (%)');abline(v=0,col='gray60')}
  if(id==12){ages<-seq(15,45,5);m<-rbind(ec$weighted_increment[match(paste(ages,'Primary'),paste(ec$age_start,ec$subtype))],ec$weighted_increment[match(paste(ages,'Secondary'),paste(ec$age_start,ec$subtype))]);barplot(m,beside=TRUE,names.arg=paste(ages,ages+4,sep='-'),col=cols[1:2],xlab='Age group',ylab='Contribution / 100,000');legend('topleft',c('Primary','Secondary'),fill=cols[1:2],bty='o',bg='white',box.col='white',inset=.02)}
 }
 names<-c('Figure1_PCOS_trends','Figure2_PCOS_subtypes','Figure3_decomposition','Figure4_population_source','Figure5_benchmark_sensitivity','FigureS1_reference_exclusions','FigureS2_benchmark_trajectories','FigureS3_composition_sensitivity','FigureS4_endometriosis_trajectory','FigureS5_country_shifts','FigureS6_terminal_country','FigureS7_terminal_age_type')
 for(i in seq_along(names)){
  tall<-i %in% c(6,8,10,11);ww<-if(i %in% c(1,2,4,7))11 else 9;hh<-if(tall)8 else 5
  pdf(file.path(out,paste0(names[i],'.pdf')),width=ww,height=hh);draw(i);dev.off()
  png(file.path(out,paste0(names[i],'.png')),width=ww,height=hh,units='in',res=160);draw(i);dev.off()
 }
 invisible(names)
}
