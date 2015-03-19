from bitstring import BitStream, BitArray
from boto.dynamodb2.table import Table
#setup user table from dynamodb
users = Table('wwusercards')
fn='codes.txt'
#formated with spaces as
#site  code  firstname  lastname

#users.put_item(data={'cardnumber':cardint, 'department':dept, 'firstname':first, 'lastname':last, 'email':email, 'cardid':cardid})
#users.put_item(data={'cardnumber':int(cardnum),'firstname':first, 'lastname':last, 'site':int(site), 'cardid':int(code)})

def parityOf(int_type):
   parity = 0
   while (int_type):
       parity = ~parity
       int_type = int_type & (int_type - 1)
   return(parity)

f = open(fn)
for line in iter(f):
    splitLine = line.split()
    site=splitLine[0]
    code=splitLine[1]
    first=splitLine[2]
    last=splitLine[3:]
    rawcard=BitArray(int=int(site), length=34)<<17 ^ BitArray(int=int(code), length=34)<<1
    fullcard = rawcard ^ BitArray(int=int(parityOf (int(rawcard.int)) & 1), length=34)
    cardnum=int(fullcard.int)
    if (len(list(users.query_2(cardnumber__eq=cardnum))) < 1):
        print "inserting: "+str(cardnum)+", "+first+" "+last+" card number: "+str(site)+"-"+str(code)
        users.put_item(data={'cardnumber':int(cardnum),'firstname':first, 'lastname':last, 'site':int(site), 'cardid':int(code)})
    else:
        print "deleting: "+str(cardnum)+", "+first+" "+last+" card number: "+str(site)+"-"+str(code)
        users.delete_item(cardnumber=cardnum)
        print "inserting: "+str(cardnum)+", "+first+" "+last+" card number: "+str(site)+"-"+str(code)
        users.put_item(data={'cardnumber':int(cardnum),'firstname':first, 'lastname':last, 'site':int(site), 'cardid':int(code)})
f.close()
