# Xcode Recipes

This folder contains fully functioning Xcode download, extraction, and Munki
recipes.

## Use Overrides to download

To download Xcode, you need to create an override with the following two input
variables:
* APPLE_ID: an AppleID that has access to the developer downloads portal
* PASSWORD_FILE: path to a text file containing the APPLE_ID password in plain
    text. This defaults to a file called "secret.txt".

*KNOWN LIMITATION: This does not work on an account with 2fa or 2-step.*

This override can be used for the .download alone, or with the .munki recipes.

## A note about version numbers

These recipes extract the major, minor, and patch versions from the version
numbers, as well as what Apple refers to as the "bundle" version, as well as
the build number. This is because Apple has, at various times, bumped a beta of
Xcode into GM version by only increasing the build number one digit, and yet
somehow still introduced functional changes.

Because of the fact that any possible release of Xcode could behave differently
than identically-numbered previous releases, we use all possible version data
to differentiate Xcode releases.

The build number is used in the Display Name only, and not included in the
version information used by Munki to determine install status.

## Recipes

### Xcode.munki Recipe

This is the "classic" Xcode Munki recipe. It will import an item into Munki
simply named "Xcode", and installs into "/Applications/Xcode.app", similar to
how the App Store version behaves.

Example output:
```
The following new items were imported into Munki:
    Name   Version           Catalogs  Pkginfo Path                                   Pkg Repo Path
    ----   -------           --------  ------------                                   -------------
    Xcode  10.2.1.14490.122  testing   apps/apple/xcode/Xcode-10.2.1.14490.122.plist  apps/apple/xcode/Xcode-10.2.1.14490.122.dmg
```

### XcodeVersionedName.munki Recipe

If you want to be able to install multiple versions of Xcode side-by-side, or
otherwise want to differentiate each version of Xcode, we can't name each
version "Xcode". Instead, each version of Xcode is named by major version.

This Munki recipe imports an item named "XcodeMajor", where the
numbers are inserted accordingly: "Xcode10".

Unlike the regular Xcode.munki recipe, this recipe also renames the .app on
disk. The app that is installed on disk is named similarly,
"/Applications/Xcode_10.2.1.app". The disk image that the recipe produces is
named similarly as well, although the DMG name is ignored by Munki as it
renames it accordingly.

Example output:
```
The following new items were imported into Munki:
    Name         Version           Catalogs  Pkginfo Path                                         Pkg Repo Path
    ----         -------           --------  ------------                                         -------------
    Xcode10  10.2.1.14490.122  testing   apps/apple/xcode/Xcode10.2.1-10.2.1.14490.122.plist  apps/apple/xcode/Xcode_10.2-10.2.1.14490.122.dmg
```

## Using Xcode.munki to get Xcode Betas
There are two possible ways to get an Xcode version, based on what you're
looking for:
* The latest Xcode Beta posted on the [Developer download portal](https://developer.apple.com/download/)
* The latest Xcode version posted in the ["More" downloads](https://developer.apple.com/download/more/) section

Xcode.download has a `BETA` input variable to determine which location it
searches. By default, `BETA` is an empty string. If you populate it with
any contents, Xcode.download will _only_ search for the Xcode URL posted on
the Developer download portal.

If `BETA` is an empty string, Xcode.download will _only_ search for the most
recently published Xcode xip file from the "More" downloads list. However,
because Apple is Apple, the latest Xcode version posted in the "More"
downloads section may be a beta, GM seed, or release.

In order to effectively limit which kind of Xcode you get, you can create
multiple overrides.

### Latest Xcode from "More" downloads
If `BETA` is empty (the default behavior), Xcode.download will look for the
latest published Xcode xip that matches the regex. As of writing time, the
most recently published Xcode is 11.2 beta 2:

![More downloads](/../screenshots/screenshots/xcode_more.png)

It may be confusing and irritating that leaving `BETA` empty still results in
obtaining a Beta release by default, but it's impossible to predict which
versions of Xcode Apple will choose to publish to the "More" list.

### Developer download portal
As of writing time, the current released beta version of Xcode is 11.2 beta 2:

![Developer download portal](/../screenshots/screenshots/xcode_beta.png)

Thus, if `BETA` is populated, this is the version that will be obtained:
```
AppleURLSearcher
{'Input': {'re_pattern': u'(.*\/Xcode_.*\/Xcode.*.xip)'}}
AppleURLSearcher: No value supplied for result_output_var_name, setting default value of: match
AppleURLSearcher: Beta flag is set, searching Apple downloads URL...
AppleURLSearcher: New fixed URL: https://developer.apple.com/services-account/download?path=/Developer_Tools/Xcode_11.2_beta_2/Xcode_11.2_beta_2.xip
{'Output': {'match': 'https://developer.apple.com/services-account/download?path=/Developer_Tools/Xcode_11.2_beta_2/Xcode_11.2_beta_2.xip'}}
```

It's predicted that Apple will only ever publish the most recent Xcode beta
here, even after a release of a newer version. As with all Apple predictions,
this behavior could change at any point.

**Override for latest beta**
For the latest release Xcode beta, you'll want to leave the `PATTERN` as is
and populate the `BETA` tag:

```
		<key>BETA</key>
		<string>Beta</string>
		<key>PATTERN</key>
		<string>(.*\/Xcode_.*\/Xcode.*.xip)</string>
```

**Override for latest non-beta**
For the latest release of any *non-beta* Xcode, change the `PATTERN` regex and
clear the `BETA` tag:

```
		<key>BETA</key>
		<string></string>
		<key>PATTERN</key>
		<string>((?!.*beta).*\/Xcode_.*\/Xcode.*.xip)</string>
```

**Override for latest Xcode of any type**
For the latest release of any type of Xcode, leave the `PATTERN` regex and
leave the `BETA` tag empty:

```
		<key>BETA</key>
		<string></string>
		<key>PATTERN</key>
		<string>(.*\/Xcode_.*\/Xcode.*.xip)</string>
```

## How It Works

### Getting the cookies
There are three custom processors that are used to get the right download data.
First, the AppleDataGatherer simply takes the AppleID & password data and writes
it out to a file, which is passed to curl. This is done to avoid having the
password show up in the process list.

The AppleCookieDownloader makes two separate curl calls. The first one sends the
login data generated by AppleDataGatherer to generate the "myacinfo" cookie
stored in "login_cookies". The second one uses the login_cookie to get access
to the download list, which generates the "download_cookies".

With the necessary cookies created, we can now access the downloads list. This
list is actually a json blob inside a gz archive, so we must use `gunzip` to
extract it, and then serialize it into JSON data. If the access creds fail, this
will be how we tell - the downloads list will actually be raw JSON indicating an
error response from the server, rather than JSON wrapped in gzip.

### Parsing the list of downloads
All of the logic is done in the AppleURLSearcher processor.

As described in the Beta section above, the behavior for obtaining the URL is
different based on whether the `BETA` tag is set. If the `BETA` input variable
is empty, then the "More" downloads list is searched.

Rather than using URLTextSearcher, the "More" downloads list is a zip-compressed
JSON blob that populates a table. The file is stored inside the AutoPkg cache,
in `%RECIPE_CACHE_DIR%/downloads/listDownloads`. You can read this file yourself
if you wish to see a full list of all information available for download.

We use regex to parse the list of download URLs for the given pattern we want.
The result will be a single download URL that can be passed to URLDownloader,
which also uses the download cookie to access the data.

If the `BETA` tag is populated, we instead use the logic from URLTextSearcher to
parse the Developer downloads page for a matching regex to an Xcode beta xip.

### Xip extraction

Hat tip to Graham Gilbert for pointing out that `xip --expand` does a great job
at extracting xips without all the hard work of using xar, cpio, or pbzx
madness.

## Important Notes

Xcode is a nasty beast. Apple has no compunction against changing it any time of
day or night, or renaming it, or breaking assumptions. Since they provide no
useful API of any kind to automate this, we have to use hacky workarounds like
this to do something straightforward like downloading software.

Be warned that it could break at any moment.

Also, Xcode is a roughly ~7 GB download, so depending on your internet, the
download portion alone could take significant time. Then, extracting the xip
into the app takes at least 10-15 minutes on an SSD drive. Then we need to
wrap the app in a disk image, which takes another 10-15 minutes depending on
your machine.
