Description
==================
cpe_munki is an umbrella cookbook to install, configure, and manage Munki.

The munkitools2.chef AutoPkg recipe will download the latest munkitools2 package, and then unpack the "Core", "Admin", and "Launchd" packages into separate files. The "App" package is left alone as it contains binaries that must be installed through an external mechanism (such as cpe_remote_pkg or Munki itself).

The AutoPkg recipe also generates the `cpe_munki_install` resource, just to provide a basic Chef resource to install Munki.

This is intended to work directly with [cpe_munki](https://github.com/facebook/IT-CPE/tree/master/chef/cookbooks/cpe_munki). You can sync in (using `rsync`, for example) the copy produced by this AutoPkg recipe directly into that cookbook.


## General workflow
To obtain the latest release version of Munkitools2:
```
$ autopkg run -v munkitools2.chef
$ rsync -Phav ~/Library/AutoPkg/com.facebook.cpe.chef.munkitools2/cpe_munki IT-CPE/chef/cookbooks/cpe_munki
```

To obtain the latest prerelease:
```
$ autopkg run -v munkitools2.chef -k INCLUDE_PRERELEASES='yes'
$ rsync -Phav ~/Library/AutoPkg/com.facebook.cpe.chef.munkitools2/cpe_munki IT-CPE/chef/cookbooks/cpe_munki
```