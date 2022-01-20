function init()
m.devAPIKey = "92D1822AE786DC4096F1A5530165121A5642"
m.uriFetcher = createObject("roSGNode", "UriFetcher")
m.store = CreateObject("roSGNode", "ChannelStore")
m.store.ObserveField("catalog", "ongetCatalog")' as Boolean
m.productGrid = m.top.FindNode("productGrid")
m.productGrid.ObserveField("itemSelected", "onProductSelected")
m.store.observeField("orderStatus", "onOrderStatus")
m.store.observeField("confirmPartnerOrderStatus", "onRequestPartnerOrderStatus")
m.store.command="getCatalog"
end function

function onRequestPartnerOrderStatus()
    print "print";m.store.confirmPartnerOrderStatus
end function

function ongetCatalog()
     data = CreateObject("roSGNode", "ContentNode")
    if (m.store.catalog <> invalid)then
        count = m.store.catalog.GetChildCount()
        for i = 0 to count - 1
            productData = data.CreateChild("ChannelStoreProductData")
            item = m.store.catalog.getChild(i)
            print "item";item
            productData.productCode = item.code
            productData.productName = item.name
            productData.productPrice = item.cost
            productData.productBought = false
              
        end for
        m.productGrid.content = data
        m.productGrid.setFocus(true)
        endif
end function

function onProductSelected() as void
    ? "!----------------------new order---------------------!"
    ? "> onProductSelected"
    index = m.productGrid.itemSelected
    m.itemSelected = m.productGrid.content.GetChild(index)
    ? "> selected product code: " m.itemSelected.productCode
    createOrder()
end function

function createOrder() as void
  ' create, process, and validate order
  myOrder = CreateObject("roSGNode", "ContentNode")
  itemPurchased = myOrder.createChild("ContentNode")
  ? "creating order ..."
  ? "> product code: " m.itemSelected
  ? "> product name: " m.itemSelected.productName
  itemPurchased.addFields({ "code": m.itemSelected.productCode, "name": m.itemSelected.productName, "qty": 1})
  m.store.order = myOrder
  ? "processing order ..."
  m.store.command = "doOrder"
end function

function onOrderStatus(msg as Object)
    status = msg.getData().status
    if status = 1 ' order success
        ? "> order success"
            tid = m.store.orderStatus.getChild(0).purchaseId
            ' validate the order by checking if it is now entitled on the roku side
            makeRequest("url", {uri: Substitute("https://apipub.roku.com/listen/transaction-service.svc/validate-transaction/{0}/{1}", m.devAPIKey, tid)}, "validateOrder")
    else 'error in doing order
        ? "> order error ..."
        ? "> error status " status ": " msg.getData().statusMessage
        m.store.order = invalid 'clear order
    end if
end function

function makeRequest(requestType as String, parameters as Object, callback as String)
    context = createObject("RoSGNode","Node")
    if type(parameters)="roAssociativeArray"
        context.addFields({parameters: parameters, response: {}})
        context.observeField("response", callback) ' response callback is request-specific
        if requestType = "url"
            m.uriFetcher.request = {context: context}
        else if requestType = "registry"
            ? "< Accessing Registry for a " parameters.command
            m.registryTask.request = {context: context}
        end if
    end if
end function

function validateOrder(msg as Object) as void
    ? "validating order ..."
    response = msg.getData()
    if response.code <> 200
        ? "Validate transaction failed, check if API key and transaction ID are valid"
        ' dialogBox = CreateObject("roSGNode", "Dialog")
        return
    end if

    xml = createObject("roXMLElement")
    xml.parse(response.content)
    isEntitled = (xml.getNamedElements("isEntitled")[0].getText() = "true")
    ? "< new purchase is entitled: " isEntitled
    if isEntitled = true
        print "order is entitled, store access token on device and grant access to user"

        'grantAccess()
    else
        ? "order is not entitled, create new subscription again"
        ' dialogBox = CreateObject("roSGNode", "Dialog")
    end if
end function

