# dCode skip cipher: start at 0-based s, step k, wrap mod L; landing on a read letter -> next unread one
BEGIN{L=length(t); split(t,ch,""); p=s%L; out=""; for(i=0;i<L;i++){while(u[p]) p=(p+1)%L; out=out ch[p+1]; u[p]=1; p=(p+k)%L} printf "%s", out}
