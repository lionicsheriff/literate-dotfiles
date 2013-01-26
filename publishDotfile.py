import os
import platform

## Set up menu item
WIKIDPAD_PLUGIN = (("MenuModifier", 1), ("MenuItemProvider", 1))
ID_CMD_PUBLISHCONFIG = "menuItem/editor/textArea/plugin/publishConfigContext/publishCurrent"


def modifyMenuV01(contextName, contextDict, menu):
    if contextName == "contextMenu/editor/textArea":
        # We want to handle this menu

        # Append a separator (if necessary)
        menu.appendNecessarySeparator()

        # We wish to append an item (this in turn calls provideMenuItemV01()
        menu.appendProvidedItem(ID_CMD_PUBLISHCONFIG)

        # Return False to inform WikidPad that we handled the menu
        return False

    # Default reaction to inform that we don't handle anything else
    return None


def provideMenuItemV01(menuItemUnifName, contextName, contextDict, menu,
        insertIdx):
    if menuItemUnifName == ID_CMD_PUBLISHCONFIG:
        # We want to provide this menu item

        # preparePlgMenuItem creates a menu item and returns it. Furthermore
        # it registers event handlers to call  evtfct  and  updatefct  if given
        theItem = menu.preparePlgMenuItem("Publish config",
                "Publishes the current page into the location specified in the location attribute",
                evtfct=cmdPublish, menuID=ID_CMD_PUBLISHCONFIG, updatefct=enableMenu)

        # Usual wxPython call to insert the item
        menu.InsertItem(insertIdx, theItem)

        # Return False to inform WikidPad that we handled the item
        return False

    # Default reaction to inform that we don't handle anything else
    return None


# menu item handler
def cmdPublish(evt, menuItemUnifName, contextName, contextDict, menu):

    txtCtrl = contextDict["txtCtrl"]
    mainCtrl = txtCtrl.getMainControl()

    metadata = getCurrentMetadata(mainCtrl)
    wiki = mainCtrl.getWikiDocument()
    publishConfig(wiki, metadata['location'][0])  # assuming you can't get here without a location


# controls whether the menu item is active
def enableMenu(evt, menuItemUnifName, contextName, contextDict, menu):
    txtCtrl = contextDict["txtCtrl"]
    metadata = getCurrentMetadata(txtCtrl.getMainControl())  # do I really need to go through the main control to get the current page?

    evt.Enable(canPublish(metadata))


## Actually do the stuff
def getCurrentMetadata(mainCtrl):
    return mainCtrl.getCurrentDocPage().getAttributes()


def getDotfileText(page):
    text = page.getLiveText()
    split = text.partition("\n\n")  # TODO: do I need to use os.linesep?
    return split[2]


def publishConfig(wiki, location):
    body = composeDotfile(wiki, location)
    writeDotfile(location, body)


def writeDotfile(path, body):
    path = os.path.expanduser(path)

    # make the directories for the file if they do not exist
    # attempting to create the directory and then apoligising is easier, and less prone to
    # race conditions than checking if the directory exists
    (dirs, _) = os.path.split(path)
    try:
        os.makedirs(dirs)
    except OSError:
        # unless there is already a directory at that path, something has probably gone wrong
        if not os.path.isdir(dirs):
            raise

    # finally write the config
    with open(path, 'w+') as file:
        file.write(body)


def composeDotfile(wiki, location):
    pages = wiki.getAttributeTriples(None, 'location', location)

    body = ""
    for page in pages:
        wikiWord = wiki.getWikiPage(page[0])
        if (canPublish(wikiWord.getAttributes())):
            body += getDotfileText(wikiWord)

    return body


def canPublish(metadata):
    isValid = True

    if "enabled" in metadata:
        isValid = isValid and testEnabled(metadata["enabled"])

    if "host" in metadata:
        isValid = isValid and testHost(metadata["host"])

    if "os" in metadata:
        isValid = isValid and testOs(metadata["os"])

    return isValid


def testOs(os):
    return platform.system() in os


def testHost(host):
    return platform.node in host.join(",").split(",")


def testEnabled(enabled):
    return "yes" in enabled
