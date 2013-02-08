from urllib import urlopen
from collections import OrderedDict
import json, datetime

sessionKey = ''


def login(email, password):
        #Accepts customer email & password
        #Returns sessionID (required for almost all functions)
        paramList = [("command", "LOGIN"),
                        ("email", email),
                        ("password", password),
                        ("developerKey", "INSERT DEVELOPER KEY HERE"),
                        ("applicationKey", "INSERT APP KEY HERE")]
        loginURL = buildCommandString(paramList)
        response = sendCommand(loginURL)
        if response["StatusCode"] == 0:
                sessionKey = str(response["SessionKey"])
        return sessionKey


def sendCommand(commandString):
        #Accepts a string containing an HTML request for the Tesco API
        #Returns a json response formatted as a dictionary
        f = urlopen(commandString)
        jsonResponse = f.read()
        f.close()
        return json.loads(jsonResponse)


def buildCommandString(optionsList):
        baseURL = "https://secure.techfortesco.com/groceryapi/restservice.aspx?"
        #Usually a dictionary does not preserve the order that keys are added to it.
        #collections.OrderedDict() does preserve this order.
        params = OrderedDict()
        #Builds a dictionary from the key:value pairs in optionsList
        for parameter in optionsList:
                params[parameter[0]]= parameter[1]
        #concatenates the keys and values into a string
        #joining them with an '&' character
        return baseURL + "&".join(["%s=%s" % (k, v) for k, v in params.items()])

        
def getIconPath(name):
        iconList = ['beer', 'carrot', 'chicken', 'coffee', 'crab', 'egg', 'fish', 'lobster', 'milk', 'onion', 'pepper', 'steak', 'sugar', 'tomato', 'wine']
        match = [icon for icon in iconList if icon in name.lower()]
        return match

        
def getFavourites(sessionKey):
        #Returns a list of favourite items
        command = "LISTFAVOURITES"
        paramList = [("command", "LISTFAVOURITES"),
                ("SESSIONKEY", sessionKey)]
        requestURL = buildCommandString(paramList)
        response = sendCommand(requestURL)
        favouriteList = []
        if response["StatusCode"] == 0:
                for fav in response["Products"]:
                        favDict = {}
                        if fav["Name"][0:6] == "Select" and fav["Name"][-6:] == "basket":
                                #Quick fix for weird bug in Tesco API
                                favDict["Name"] = str(fav["Name"][6:-16])
                        else:
                                favDict["Name"] = str(fav["Name"])
                        imageMatch = getIconPath(favDict["Name"])
                        if len(imageMatch) > 0:
                                favDict["ImagePath"] = '/static/icons/'+imageMatch[0]+'.png'
                        else:
                                favDict["ImagePath"] = str(fav["ImagePath"])            
                        favDict["Price"] = str(fav["Price"])
                        favDict["UnitType"] = str(fav["UnitType"])
                        favDict["ProductId"] = str(fav["ProductId"])
                        favouriteList.append(favDict)
                return favouriteList
        else:
                return response["StatusInfo"]


def modifyBasket(sessionKey, productID, amount=1):
            #Adds a product to the cart
            #If amount < 0, product will be removed instead
            paramList = [("command", "CHANGEBASKET"),
                                ("PRODUCTID", productID),
                                ("CHANGEQUANTITY", amount),
                                ("SUBSTIUTION", "NO"),
                                ("NOTESFORSHOPPER", "%20"),
                                ("SESSIONKEY", sessionKey)]
            requestURL = buildCommandString(paramList)
            response = sendCommand(requestURL)

            if response["StatusCode"] == 0:
                return amount
            else:
                return response["StatusInfo"]


def getDeliveryDates(sessionKey):
            #Returns delivery dates & prices
            #Returns so much information it crashes Python without processing!
            paramList = [("command","LISTDELIVERYSLOTS"),
                         ("SESSIONKEY", sessionKey)]
            requestURL = buildCommandString(paramList)
            response = sendCommand(requestURL)

            if response["StatusCode"] == 0:
                        slotList = []
                        for deliverySlot in response["DeliverySlots"]:
                                slotList.append((str(deliverySlot["DeliverySlotId"]),
                                                datetime.datetime.strptime ((str(deliverySlot["SlotDateTimeStart"])[:-6]), '%Y-%m-%d'),
                                                datetime.datetime.strptime ((str(deliverySlot["SlotDateTimeStart"])[11:]), '%H:%M'),
                                                datetime.datetime.strptime ((str(deliverySlot["SlotDateTimeEnd"])[11:]), '%H:%M'),
                                                str(deliverySlot["ServiceCharge"])))
                        return slotList
            else:
                return response["StatusInfo"]

#Returns a list of tuples in the form:
#(name, image url, unit price, price, quantity, unit type)
#All returned items are stored as strings
#Example output:
#[('Tesco 2 Garlic And Coriander Naan Bread',
#'http://img.tesco.com/Groceries/pi/008/5018374024008/IDShot_60x60.jpg',
#'0', '0.8', '1', #''), ('Pataks Butter Chicken Cooking 450G',
#'http://img.tesco.com/Groceries/pi/169/5011308004169/IDShot_60x60.jpg',
#'0',... etc)]
def getShoppingCart(sessionKey):
        #Returns a list of dictionarys: [{},{},{}...]
        #Each dictionary represents a line of the user's basket
        #And contains the ProductId, Name, ImagePath etc.
        paramList = [("command", "LISTBASKET"),
                        ("FAST", "N"),
                        ("SESSIONKEY", sessionKey)]
        requestURL = buildCommandString(paramList)
        response = sendCommand(requestURL)
        if response["StatusCode"] == 0:
                itemList = []
                for product in response["BasketLines"]:
                        itemDict = {}
                        itemDict["ProductId"] = str(product["ProductId"])
                        itemDict["Name"] = str(product["Name"])
                        imageMatch = getIconPath(itemDict["Name"])
                        if len(imageMatch) > 0:
                                itemDict["ImagePath"] = '/static/icons/'+imageMatch[0]+'.png'
                        else:
                                itemDict["ImagePath"] = str(product["ImagePath"])
                        itemDict["UnitPrice"] = str(product["UnitPrice"])
                        itemDict["Price"] = str(product["Price"])
                        itemDict["BasketLineQuantity"] = str(product["BasketLineQuantity"])
                        itemDict["UnitType"] = str(product["UnitType"])
                        itemList.append(itemDict)
                return itemList
        else:
                return response["StatusInfo"]

                
def getShoppingCartSummary(sessionKey):
        paramList = [("command", "LISTBASKET"), ("FAST", "N"), ("SESSIONKEY", sessionKey)]
        requestURL = buildCommandString(paramList)
        response = sendCommand(requestURL)
        cartSummary = {}
        
        if (response["StatusCode"] == 0) or (response["StatusCode"] == 140):
                cartSummary["BasketGuideMultiBuySavings"] = str(response["BasketGuideMultiBuySavings"])
                cartSummary["BasketGuidePrice"] = str(response["BasketGuidePrice"])
                cartSummary["BasketQuantity"] = str(response["BasketQuantity"])
                return cartSummary
        else:
                return response["StatusInfo"]
