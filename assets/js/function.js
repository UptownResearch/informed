// KEJR7RWVDD3ZKRM1HBCUSNS2BTZG4JQSZA   : new
// PBW8JXKSC8WXM9UPJGY72RPJ61YGEG1M6A   : mine
// https://www.4byte.directory/api/v1/signatures/

const transactionView = async () => {
    var signUrl = "https://www.4byte.directory/api/v1/signatures/?hex_signature=";

    // const resp = await fetch("https://www.4byte.directory/api/v1/signatures/");
    // const signObj = await resp.json();
    // console.log(signObj.results);

    var address = document.getElementById("address").value;

    var url = "https://api.etherscan.io/api?module=account&action=txlist&address=";
    url = url.concat(address);
    url = url.concat("&startblock=0&endblock=999999999&page=1&offset=300&sort=asc&apikey=KEJR7RWVDD3ZKRM1HBCUSNS2BTZG4JQSZA");

    const response = await fetch(url);
    const myJson = await response.json();
    
    var obj = myJson.result;

    $(document).ready(function () {
        var funcAddr = '';
        var signText = '';
        var html = '<table class="table table-striped">';
        html += '<tr>';
        var flag = 0;
        $.each(obj[0], function(index, value){
            if(index != "input")
                html += '<th>'+index+'</th>';
        });
        html += '<th>'+"function"+'</th>';
        html += '</tr>';
        var asynCnt = 0;
        $.each(obj, async function(index, value){
            var subHtml = '<tr>';
            // html += '<tr>';
            $.each(value, function(index2, value2){
                if(index2 != "input")
                    subHtml += '<td>'+value2+'</td>';
                else {
                    funcAddr = value2.substr(0, 10);
                    // signText = getSignatureText(signObj.results, funcAddr);
               }
           });
           var resp = await fetch(signUrl.concat(funcAddr));
           var signObj = await resp.json();
           if(signObj && signObj.results[0] && signObj.results[0].text_signature)
               signText = signObj.results[0].text_signature;
           console.log(signText);

           subHtml += '<td>'+signText+'</td>';
           subHtml += '</tr>';
           html += subHtml;
           asynCnt++;
        $('div').html(html);
    });
        // await until(_ => asynCnt == 10);
        // html += '</table>';
        // $('div').html(html);
    });
}

function until(conditionFunction) {
    const poll = resolve => {
      if(conditionFunction()) resolve();
      else setTimeout(_ => poll(resolve), 10);
    }
  
    return new Promise(poll);
  }

const openseaFilter = () => {
    
}