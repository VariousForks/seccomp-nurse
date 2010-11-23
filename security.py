#! /usr/bin/env python

import logging, os
securitylog = logging.getLogger("sandbox.security")

def inrange(addr, section_range):
    a,b = section_range
    return a <= addr < b

class SecurityManager(object):
    def __init__(self, mappings, fs_root='/'):
        self.protectedareas = mappings
        self.fs_root  = fs_root
        self.fd_table = {}
        self.fs_whitelist = ['/etc', '/usr', '/bin', '/tmp']

    def register_descriptor(self, fd, filename):
        if fd in self.fd_table:
            securitylog.error('File descriptor %d already opened!' % fd)
            return False
        self.fd_table[fd] = filename
        securitylog.debug('Registering file descriptor %d associated to %s' % (fd, filename))
        return True

    # Trying to close a not-opened-file-descriptor is not
    # fatal because daemons usually try to close every
    # file descriptors at init.
    def unregister_descriptor(self, fd):
        opened = fd in self.fd_table
        if opened:
            del(self.fd_table[fd])
        return opened

    def open(self, filename, perms, mode):
        return self.is_valid_path(filename)

    def close(self, fd):
        return True

    def access(self, path, mode):
        return self.is_valid_path(filename)

    def getcwd(self, ptr):
        return self.is_valid(ptr) # XXX

    def getpgrp(self):
        return True # XXX

    def ugetrlimit(self, ptr):
        return self.is_valid(ptr) # XXX

    def gettimeofday(self, tvptr, tzptr):
        return self.is_valid(tvptr) and self.is_valid(tzptr) # XXX

    def brk(self, addr):
        return self.is_valid(addr) # XXX

    def munmap(self, addr, length):
        return self.is_valid(addr) and self.is_valid(addr+length)

    def fstat(self, fd, ptr):
        ret = self.is_valid(ptr) and ((0 <= fd <= 2) or (fd in self.fd_table))
        securitylog.debug('Can fstat(%d)? %s' % (fd, ret))
        return ret

    def mmap2(self, addr, length, prot, flags, fd, pgoffset):
        if addr != 0:
            if not (self.is_valid(addr) and self.is_valid(addr+length)):
                securitylog.debug('mmap2() => invalid address: %#x' % addr)
                return False
        return True

    def mmap(self, addr, length, prot, flags, fd, offset):
        if addr != 0:
            if not (self.is_valid(addr) and self.is_valid(addr+length)):
                securitylog.debug('mmap() => invalid address: %#x' % addr)
                return False
        return True

    def is_valid(self, ptr):
        ret = True
        for area in self.protectedareas:
            if inrange(ptr, area):
                ret=False
                break
        if not ret:
            securitylog.error('invalid pointer supplied: %#x' % ptr)
        return ret

    def is_valid_path(self, filename):
        path = os.path.realpath(filename)
        for authorized_path in self.fs_whitelist:
            if path.startswith(authorized_path):
                return True
        return False

    def lseek(self, fd, offset, whence):
        return True # XXX

    def llseek(self, fd, offset_high, offset_low, result, whence):
        return self.is_valid(result) # XXX

    def readlink(self, bufptr):
        return self.is_valid(bufptr) # XXX

    def time(self, bufptr):
        return self.is_valid(bufptr) # XXX

    def times(self, bufptr):
        return self.is_valid(bufptr) # XXX

    def stat64(self, path, addr):
        return self.is_valid(addr) # XXX

    def access(self, path, mode):
        return True # XXX

