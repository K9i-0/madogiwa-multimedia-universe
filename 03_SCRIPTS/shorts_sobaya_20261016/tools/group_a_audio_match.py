"""Timestamp-preserving reference-audio alignment used for group A captions.
Requires NumPy and SciPy. Set BLAS/OMP threads to 1 in constrained environments.
"""
import subprocess,numpy as np
from scipy.signal import correlate,stft
SR=8000
def wav(p):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(p),'-vn','-af','aresample=async=1:first_pts=0','-ac','1','-ar',str(SR),'-f','f32le','-']),dtype=np.float32)
def bounds(a):
 hop=80;n=len(a)//hop;e=np.sqrt(np.mean(a[:n*hop].reshape(n,hop)**2,axis=1));on=np.where(e>max(e.max()*.08,.002))[0];return (max(0,on[0]/100-.05),min(len(a)/SR,(on[-1]+1)/100+.1)) if len(on) else (0,len(a)/SR)
def waveform(src,ref,start=0,end=None):
 i0=max(0,int(start*SR));i1=min(len(src),int(end*SR)) if end else len(src);a=src[i0:i1].astype('float64');b=ref.astype('float64');n=len(b);b-=b.mean()
 if len(a)<n:return None
 c=correlate(a,b,mode='valid',method='fft');cs=np.r_[0,np.cumsum(a*a)];power=np.maximum(cs[n:]-cs[:-n],1e-8);score=c/np.sqrt(power*np.sum(b*b));k=int(np.argmax(score));return (i0+k)/SR,float(score[k])
def spec(a):
 _,_,z=stft(a,fs=SR,nperseg=256,noverlap=176,boundary='zeros');power=abs(z)**2;edges=np.unique(np.round(np.geomspace(2,128,25)).astype(int));return np.stack([np.log(np.maximum(power[a:b].mean(0),1e-10)) for a,b in zip(edges[:-1],edges[1:])]).astype('float64')
def spectral(ss,rs,start=0,end=None):
 i0=max(0,int(start*100));i1=min(ss.shape[1],int(end*100)) if end else ss.shape[1];a=ss[:,i0:i1];n=rs.shape[1]
 if a.shape[1]<n:return None
 b=rs-rs.mean(axis=1,keepdims=True);c=sum(correlate(a[i],b[i],mode='valid',method='fft') for i in range(len(a)));p=np.zeros(len(c))
 for ai in a:
  cs=np.r_[0,np.cumsum(ai)];cs2=np.r_[0,np.cumsum(ai**2)];p+=(cs2[n:]-cs2[:-n])-(cs[n:]-cs[:-n])**2/n
 score=c/np.sqrt(np.maximum(p,1e-6)*np.sum(b*b));score[p<.1]=0;k=int(np.argmax(score));return (i0+k)/100,float(score[k])
