const CONFIG_SECRET = "CHANGE_THIS_SECRET";

function doGet(e) {
  return json_({ok:true, service:"AI Sotuvchi"});
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || "{}");
    if (body.secret !== CONFIG_SECRET) {
      return json_({ok:false,error:"Unauthorized"});
    }

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const action = body.action;

    if (action === "products") {
      const sh = ss.getSheetByName("Products");
      const values = sh.getDataRange().getValues();
      const headers = values.shift();
      const products = values.map(r => {
        const o = {};
        headers.forEach((h,i)=>o[String(h)] = r[i]);
        return o;
      }).filter(p => String(p.active).toLowerCase() !== "false");
      return json_({ok:true, products});
    }

    if (action === "order") {
      const sh = ss.getSheetByName("Orders");
      sh.appendRow([
        body.order_id || "",
        new Date(),
        body.customer_name || "",
        body.phone || "",
        body.address || "",
        body.product || "",
        body.quantity || 1,
        body.total || "",
        body.status || "NEW",
        body.telegram_user_id || ""
      ]);
      return json_({ok:true});
    }

    return json_({ok:false,error:"Unknown action"});
  } catch (err) {
    return json_({ok:false,error:String(err)});
  }
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
