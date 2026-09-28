"""IPS encoding and application, including expanded ROMs."""
def ips_extended(old,new):
    out=bytearray(b'PATCH');p=0
    while p<len(new):
        if p<len(old) and old[p]==new[p]:p+=1;continue
        st=p;p+=1
        while p<len(new) and p-st<65535:
            if p<len(old) and old[p:p+8]==new[p:p+8]:break
            p+=1
        part=new[st:p];out.extend(st.to_bytes(3,'big'))
        if len(set(part))==1 and len(part)>3:out.extend(b'\0\0'+len(part).to_bytes(2,'big')+part[:1])
        else:out.extend(len(part).to_bytes(2,'big')+part)
    return bytes(out+b'EOF')

def apply_patch(old,patch):
    b=bytearray(old);p=5
    while patch[p:p+3]!=b'EOF':
        a=int.from_bytes(patch[p:p+3],'big');n=int.from_bytes(patch[p+3:p+5],'big');p+=5
        if not n:n=int.from_bytes(patch[p:p+2],'big');data=patch[p+2:p+3]*n;p+=3
        else:data=patch[p:p+n];p+=n
        if len(b)<a+n:b.extend(bytes(a+n-len(b)))
        b[a:a+n]=data
    return bytes(b)
