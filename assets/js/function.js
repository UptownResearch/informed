const transactionView = async () => {
    var address = document.getElementById("address").value;

    var url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=";
    url = url.concat(address);
    url = url.concat("&startblock=0&endblock=999999999&page=1&offset=1000&sort=asc&apikey=KEJR7RWVDD3ZKRM1HBCUSNS2BTZG4JQSZA");
    // alert(url);
    const response = await fetch(url);
    const myJson = await response.json();
    
    var obj = myJson.result;
    console.log(obj);

    $(document).ready(function () {
        var html = '<table class="table table-striped">';
        html += '<tr>';
        var flag = 0;
        $.each(obj[0], function(index, value){
            html += '<th>'+index+'</th>';
        });
        html += '</tr>';
         $.each(obj, function(index, value){
             html += '<tr>';
            $.each(value, function(index2, value2){
                html += '<td>'+value2+'</td>';
            });
            html += '<tr>';
         });
         html += '</table>';
         $('div').html(html);
    });
}
// KEJR7RWVDD3ZKRM1HBCUSNS2BTZG4JQSZA   : new
// PBW8JXKSC8WXM9UPJGY72RPJ61YGEG1M6A   : mine