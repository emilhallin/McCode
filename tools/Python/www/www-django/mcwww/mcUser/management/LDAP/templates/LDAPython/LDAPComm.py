#=======================================================================================#
# LDAPComm                                                                              #
# --------                                                                              #
# ldapAdd:                                                                              #
#   takes LDIF file path, authenticating dn, and, authenticating password as arguments  #
#   reports the action to be taken to the user                                          #
#   tries to perform and catches and reports if there is an error.                      #
# ldapMod(V):                                                                           #
#   takes LDIF file path, authenticating dn, and, authenticating password as arguments  #
#   reports the action to be taken to the user                                          #
#   tries to perform and catches and reports if there is an error.                      #
# ldapSYSROOTmod:                                                                       #
#   uses the system root authentication to provide ldapMod functionality.               #
#   Limited use. LDAPs authentication takes precedent over sys for a number of cases.   #
# ldapQuery:                                                                            #
#   builds outfile based on user credentials and query                                  #
#   tries to query the DB, errors thrown are captured in the outfile too                #
#   (should only throw query errors, check this and handle properly?)                   #
# ldapAdminGroupQuery:                                                                  #
#   Takes a dn and pw of LDAP entity and queries the DB for itStaff and courseStaff     #
#   groups, filters the result through grep for the cn of the dn and retunrs true if    #
#   the entry is a member of Staff groups, or false if not. This does not mean the LDAP #
#   entry has modify permissions.                                                       #
# authenticateMcUser:                                                                   #
#   Takes auth_cn and auth_pw as argument, checks the LDAP DB ldapwhoami to check       #
#   existence returns boolean based on existence of user.                               #
# ------------------                                                                    #
# Author: Mark Lewis                                                                    #
#=======================================================================================#
from subprocess import call,check_output,Popen,PIPE
import traceback
from re import split
import sys

from cStringIO import StringIO

class LDAPComm:
#=======================================================================================#
# Builds an access log file and sets the query counter to zero.
#=======================================================================================#
    def __init__(self):
        from time import strftime as t
        file_loc = "mcUser/management/LDAP/LDAP_access/access.txt"
        self.access_file = open(file_loc, 'a+')
        self.access_file.write("LDAPComm instantiated: %s @ %s\n"% (t("%H:%M:%S"), t("%d/%m/%Y")))
        self.query_num = 0
#================#
# Access logging #
#================#
    def log(self, log_str):
        self.access_file.write(log_str+"\n")
#=======================================================================================#
# Modification method: 
#=======================================================================================#
# General ldapAdd #
#=================#
    def ldapAdd(self, ldif_file, auth_dn, auth_pw):
        cn = split(",", auth_dn)[0]
        try:
            fid = Popen(["ldapadd", "-x", "-D", auth_dn, "-f", ldif_file, "-w", auth_pw],
                        stdout = PIPE,
                        stderr = PIPE)
            stdout, stderr = fid.communicate()
            self.log("%s ADDED from : %s\nstdout:\n%s" % (cn, ldif_file, stdout))
        except:
            self.log("Error adding %s: %s" % (ldif_file,stderr))
            self.log("Backtrace: %s" % traceback.format_exc()) #sys.exc_info())
#=================#
# General ldapMod #
#=================#
    def ldapMod(self, ldif_file, auth_dn, auth_pw):
        cn = split(",", auth_dn)[0]
        self.log("%s MODIFICATION with: ldapmodify -x -D %s -f %s -w PASSWORD" % cn, auth_dn, ldif_file) 
        try:
            fid = Popen(["ldapmodify", "-x", "-D", auth_dn, "-f", ldif_file, "-w", auth_pw],
                        stdout=PIPE,
                        stderr=PIPE)
            stdout,stderr = fid.communicate()
            if 'modifying' in stdout:
                self.log("%s MODIFIED: ldapadd -x -D %s -f %s -w PASSWORD" % (cn, auth_dn, ldif_file))
            else:
                self.log("Error modifying %s: %s" % (cn,stderr))
                print "Error:%s \n Backtrace:%s" % (stderr, traceback.format_exc())
        except:
            self.log("ldapMod Error: %s" % str(sys.exc_info()))

#=================#
# Verbose ldapMod #
#=================#
    def ldapModV(self, ldif_file, auth_dn, auth_pw):
        cn = split(",", auth_dn)[0]
        self.log("%s MODIFY attempt with: %s" % ldif_file)
        try:
            fid = Popen(["ldapmodify", "-x", "-D", auth_dn, "-f", ldif_file, "-w", auth_pw, "-v"],
                        stdout=PIPE,
                        stderr=PIPE)
            stdout,stderr = fid.communicate()
            if 'modifying' in stdout:
                self.log("%s MODIFIED: ldapadd -x -D %s -f %s -w PASSWORD" % (cn, auth_dn, ldif_file))
            else:
                self.log("Error modifying %s: %s" % (cn,stderr))
                print "Error:%s \n Backtrace:%s" % (stderr, traceback.format_exc())
        except:
            self.log("ldapMod Error: %s" % sys.exc_info()[0])
#=======================================================================================#
# This is a bit of a powerful thing to put in the build script but it should be ok. 
# As it's going to go in the build script then we should actually remove the sudo later
#=======================================================================================#
    def ldapSYSROOTmod(self, ldif_file):
        self.log("\nsudo ldapadd -Y EXTERNAL -H ldapi:/// -f config_pw_slapadd.ldif")
        try:
            self.log("MODIFICATION attempt of ROOTPWD: %s" % ldif_file)
            fid = Popen(["sudo", "ldapadd", "-Y", "EXTERNAL", "-H", "ldapi:///", "-f", ldif_file, "-v"],
                        stdout=PIPE,
                        stderr=PIPE)
            stdout,stderr = fid.communicate()
            self.log("stdout: %s" % stdout)
        except:
            self.log("Error creating LDAP ROOT user pswd: %s \n" % str(sys.exc_info()))
#=======================================================================================#
# Query Methods
#=======================================================================================#
# General Query #
#===============#
    def ldapQuery(self, auth_dn, auth_pw, query):
        cn = split(",", auth_dn)[0]
        self.query_num += 1
        log_str = cn+" #"+str(self.query_num)+" QUERY with: ldapsearch -LLL -b DN -D "+auth_dn+" -w PASSWORD "+query+"\n"
        self.log("\n%s" % log_str)
        try:
            fid = Popen(["ldapsearch", "-LLL", "-b", "DN", "-D", auth_dn, "-w", auth_pw, query],
                        stdout=PIPE,
                        stderr=PIPE)
            stdout,stderr = fid.communicate()
        except:
            self.log("Error:")
            for err_item in sys.exc_info():
                self.log(err_item)
            pass
        return stdout.split("\n")
#==========================#
# Check existence in group #
#==========================#
    def ldapAdminGroupQuery(self, auth_cn):
        self.query_num += 1
        if not 'cn=' in auth_cn:
            auth_cn = "cn=%s" % auth_cn
        query = "(|(cn=itStaff)(cn=courseStaff))"
        self.log("\n%s #%s AUTH ACCESS QUERY: %s\n" % (auth_cn, str(self.query_num), query) )
        try:
            fid = Popen(
                ["ldapsearch", "-LLL", "-b", "DN", "-D", "cn=DummyUser,ou=person,DN", "-w", "DummyPW", query],
                stdout=PIPE,
                stderr=PIPE)
            stdout,stderr = fid.communicate()
            if cn in stdout:
                return True
            else:
                self.log("LDAP privs insufficient: %s" % stderr)
                return False
        except:
            self.log("Incorrect search profile: %s => %s" % (query, sys.exc_info()[0]))
            return False
#=====================#
# User Identification #
#=====================#
    def ldapAuthenticate(self, auth_cn, auth_pw):
        try:
            dn = "cn=\"" + auth_cn + "\",ou=person,DN"
            try:
                fid = Popen(["ldapwhoami", "-vvv", "-D", dn, "-x", "-w", auth_pw],
                            stdout=PIPE,
                            stderr=PIPE)
                stdout,stderr = fid.communicate()
                if "Success" in stdout:
                    self.log("%s may access LDAP.\n"%dn)
                    return True
                else:
                    self.log("Access attempt by %s unsuccessful: %s\n" % (dn, stderr))
                    return False
            except:
                self.log("Access attempt by %s exception: %s\n" % (dn, str(sys.exc_info())))
                ''' MESSAGE BOX SUGGESTING ERROR '''
                return False
        except:
            self.log("ERROR: cn not supplied.\n")
