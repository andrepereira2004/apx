# Thunderbird tiled sidebar

Owner clarified that the prior Send design was accepted; reverted only the last
Send-specific change. Preserved the rest of the accepted compose layout.

Root cause: native vertical layout squeezes folders to100px to preserve300px
minimums for both message list and reading pane. In half-window tiling that
makes folder names and New Message illegible. CSS in graphite.css now retains
219px minimum folders, and at <=1100px stacks reading below list in vertical
layout. Native classic/wide modes and account-central keep their respective
layouts with readable sidebar. Wide vertical windows retain native splitters.
Narrow vertical reading/list split is40/60 and its native width-resizing handle
is hidden, since it would act along the wrong axis. F8/collapse and folder-pane
collapse remain supported. No Hyprland rule or account/preference changes.

Validation: isolated offline native155 profile;758px client with234px folders,
message below list and no horizontal overflow;1536px client with three columns
and live splitter. Message-pane collapse expands list. Screenshots and computed
geometry saved here. Test profile/control endpoint closed and profile removed.
Source/profile byte match verified. No live mail content captured.

Applied to faculdade existing default-release profile only. Backups use the
existing appearance installer inventory. Existing live drafts/windows preserved;
a full Thunderbird restart is needed for the new CSS. Owner visual acceptance
pending. No commit/push.
