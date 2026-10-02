---
product: LGA ToolPack-B
release_repo: legandrop/LGA_ToolPack_B-for_Nuke
tech_changelog: ChangeLog.md
version_heading: "## v{v}"
platforms: [win, mac]
---
# What's new in LGA ToolPack-B
<!-- Editable while a version is unpublished. NOT append-only. Published versions are frozen. -->

## Unreleased

## v1.09
- [fixed] CDL -> CC Input Process no longer uses a node left selected inside a gizmo when nothing is selected in the Node Graph, and says so when no valid node is selected.
- [new] AMF (NODE BUILDS) builds the shot's color chain from its .amf file, asks which .amf to use when the shot has more than one, and can also leave a copy as the Viewer's Input Process.
- [fixed] Animation Maker opens again from its right-click menu, and the buttons it adds to a node's tab work again, instead of failing with a name error.
- [improved] Animation Maker is updated to version 1.5, with Nuke 16 support.
- [improved] Enable Tools has a new look: larger text, rounded checkboxes, a clickable config path that opens your default file manager, and a window that opens at the height it needs.
- [improved] CopyCat Cleaner, Update Folder Favs, Media Missing Frames and the pack's message dialogs share a unified dark look, and Update Folder Favs now puts its action button last.
