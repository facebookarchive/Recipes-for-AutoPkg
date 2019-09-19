# Shared Processors

## FileAppender

This processor will simply append a string on to the end of a file.  This is useful if an AutoPkg recipe needs to add more variables or other data into a file that already exists (as part of a download, or something created from a previous FileCreator processor).

### Example Usage:
```
    <dict>
      <key>Processor</key>
      <string>com.facebook.autopkg.shared/FileAppender</string>
      <key>Arguments</key>
      <dict>
        <key>file_path</key>
        <string>%pkgroot%/attributes/default.rb</string>
        <key>file_content</key>
        <string>this_will_be_added_to_the_end</string>
      </dict>
    </dict>
```

## PackageInfoVersioner

This processor provides a way to get a version number from the PackageInfo file inside a distribution/bundle style package.  This processor specifically looks for the "pkg-info" XML tag inside the PackageInfo file and uses that as the version.  This is helpful for bundle packages that provide multiple components with unique / differing version numbers, and there's no single item you can reliably use for versioning.

The simplest usage is to use something like FileFinder to locate the PackageInfo file inside the bundle package you've downloaded or unarchived and then call this processor.

### Example Usage:
```
    <dict>
      <key>Processor</key>
      <string>com.facebook.autopkg.shared/PackageInfoVersioner</string>
      <key>Arguments</key>
      <dict>
        <key>package_info_path</key>
        <string>%found_filename%/PackageInfo</string>
      </dict>
    </dict>
```

## Rsync

This processor calls out to a locally installed rsync (defaults to `/usr/bin/rsync`) to rsync between a source and destination.  You can specify a path to a specific rsync binary if needed.  

Arguments can be passed in, and the string provided to the "rsync_arguments" processor input variable will be passed directly into the subprocess call to rsync. See the rsync man page for acceptable arguments.  *NOTE: The leading hyphens before your arguments are required!*

Please note that we have so far only used this for local source -> destination copying, and have not tested a very wide a variety of rsync arguments - so there may be some things that get passed in that don't behave properly in this context.  If you do find some arguments that cause problems, please let us know!

### Example Usage:
```
    <dict>
      <key>Processor</key>
      <string>com.facebook.autopkg.shared/Rsync</string>
      <key>Arguments</key>
      <dict>
        <key>source_path</key>
        <string>%RECIPE_CACHE_DIR%/unpack/folder</string>
        <key>destination_path</key>
        <string>%pkgroot%/merged_folder</string>
        <key>rsync_arguments</key>
        <string>-Phav</string>
      </dict>
    </dict>
```

## SHAChecksum

This processors calls out to `/usr/bin/shasum` to calculate a checksum on a file.  You can specify the SHA type (to be passed to the `-a` argument) as an input variable.

### Example Usage:
This example will calculate the SHA-256 sum:

```
    <dict>
      <key>Processor</key>
      <string>com.facebook.autopkg.shared/SHAChecksum</string>
      <key>Comment</key>
      <string>Calculate SHA256 checksum</string>
      <key>Arguments</key>
      <dict>
          <key>source_file</key>
          <string>%RECIPE_CACHE_DIR%/%NAME%-%version%.pkg</string>
          <key>checksum_type</key>
          <string>256</string>
      </dict>
    </dict>
```

## SubDirectoryList
This is a more complex processor with more specific usage.  For a given root path, this processor will walk through and create two lists: one for all files found relative to the root path, and one for all directories found relative to the root path.

Both of these lists are stored as strings, with each item separated by the contents of the "suffix_string" input variable (which defaults to "," comma).

This doesn't have too much use in most AutoPkg recipes, but is the foundational key for translating packages into other management suites that require the pre-creation of subdirectories before placing files on the disk.

### Example Usage:
Here's a simple example for how to get the list of contents inside an unpacked package - such as the Munki app package.

```
    <dict>
      <key>Processor</key>
      <string>com.facebook.autopkg.shared/SubDirectoryList</string>
      <key>Comment</key>
      <string>MUNKI ADMIN - get list of folder contents</string>
      <key>Arguments</key>
      <dict>
        <key>root_path</key>
        <string>%pkgroot%/files/default/munki/admin/%version%/</string>
      </dict>
    </dict>
```
The resulting `%found_directories%` will contain a list of all folders that are inside this root path, and the `%found_files%` will contain a list of all files that were found.

This could be useful for recipes that convert packages into Puppet or Chef recipes, which may require directories to be created on disk prior to files being placed there.
