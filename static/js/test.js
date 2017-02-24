(function () {

    /**
 * Created by Administrator on 12/8/2016.
 */
    Date.prototype.Format = function (formatStr) {
        var str = formatStr;
        var week = ['日', '一', '二', '三', '四', '五', '六'];
        str = str.replace(/yyyy|YYYY/, this.getFullYear());
        str = str.replace(/yy|YY/, (this.getYear() % 100) > 9 ? (this.getYear() % 100).toString() : '0' + (this.getYear() % 100));
        str = str.replace(/MM/, (this.getMonth() + 1) > 9 ? (this.getMonth() + 1).toString() : '0' + (this.getMonth() + 1));
        str = str.replace(/M/g, (this.getMonth() + 1));
        str = str.replace(/w|W/g, week[this.getDay()]);
        str = str.replace(/dd|DD/, this.getDate() > 9 ? this.getDate().toString() : '0' + this.getDate());
        str = str.replace(/d|D/g, this.getDate());
        str = str.replace(/hh|HH/, this.getHours() > 9 ? this.getHours().toString() : '0' + this.getHours());
        str = str.replace(/h|H/g, this.getHours());
        str = str.replace(/mm/, this.getMinutes() > 9 ? this.getMinutes().toString() : '0' + this.getMinutes());
        str = str.replace(/m/g, this.getMinutes());
        str = str.replace(/ss|SS/, this.getSeconds() > 9 ? this.getSeconds().toString() : '0' + this.getSeconds());
        str = str.replace(/s|S/g, this.getSeconds());
        return str;
    }
    $.ajaxSetup({
        global: true,
        type: 'POST',
        dataType: 'json',
        processData: false,
        contentType: 'application/json',
        timeout: 1800000,
        //timeout: 6000,
        error: function (xhr, textStatus, errorThrown) {
            if (this.loadingTimer) {
                clearTimeout(this.loadingTimer);
            }
        },
        beforeSend: function () {
            var me = this;
            this.data = JSON.stringify(this.data);
        },
        complete: function () {
        }
    });
    var now  = new Date(),data = null;
    now.setDate(now.getDate()+21);
    var daysStore = 0,citiesSettings = [],domesticCity=null;
    function getNextDateArray(days) {
    //    days += daysStore;
        var timeArray = [];

        for(var i =0;i<days;i++){
            now.setDate(now.getDate()+1);
            timeArray.push(now.Format("yyyy-MM-dd"));
        }
    //    daysStore = days;
        return timeArray;
    }
    function showChart(dates,citiesFlights) {
             Highcharts.chart('container', {
                title: {
                    text: 'AirAsia Prices',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Source:Scrawl WebSite',
                    x: -20
                },
                xAxis: {
                    categories: dates
                },
                yAxis: {
                    title: {
                        text: 'CNY'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    valueSuffix: 'CNY'
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series:citiesFlights,
                plotOptions: {
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function (e) {
                                    hs.htmlExpand(null, {
                                        pageOrigin: {
                                            x: e.pageX || e.clientX,
                                            y: e.pageY || e.clientY
                                        },
                                        headingText: this.series.name,
                                        maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
                                            this.y + ' visits',
                                        width: 200
                                    });
                                }
                            }
                        },
                        marker: {
                            lineWidth: 1
                        }
                    }
                },
            });
    }

    function getCitiesFlights(dates) {
             var citiesFlights = [];
               for(var i=0,len = data.result.length;i<len;i++){
                   var flight = data.result[i];
                   if(domesticCity === null) continue;
                   if(citiesSettings.indexOf(flight.to) === -1 && domesticCity === flight.from) continue;
                   var flightPrices = [];
                   for(var j=0,len2 = dates.length;j<len2;j++){
                      if( flight.data[dates[j]]){
                          flightPrices.push(parseFloat(flight.data[dates[j]].price));
                      }else{
                          flightPrices.push(0);
                      }
                   }
                   citiesFlights.push({
                       name:flight.fromDesc +"-"+flight.toDesc,
                       data:flightPrices
                   })
               }
               return citiesFlights;
    }

    function refreshChart(days) {
         if(data === null)return;
                var dates  = getNextDateArray(days);
               showChart(dates,getCitiesFlights(dates));
    }

    $(function () {
         $(".pre").click(function () {
             if(data === null)return;
             now.setDate(now.getDate()-30);
             $(".next").click();
         });
         $(".next").click(function () {
            refreshChart(15);
         });
         $("body").on("click",".refresh",function () {
            var selectedCity = $("input[name='selectedCity']:checked");
            var allCountries = $("input[name='selectedCities']:checked");
            if(selectedCity.length&&allCountries.length){
                citiesSettings = [];
                allCountries.each(function () {
                   citiesSettings.push( $(this).val());
                });
                domesticCity = selectedCity.val();
                  if(data === null)return;
                 now.setDate(now.getDate()-15);
                 $(".next").click();
            }
         });
       $.ajax({
           url:"/airasia/api/flights",
           type:'get',
           success:function (result) {
               data  = result;
                $(".next").click();
                var html = $.templates("#countries").render(result);
                $("#condition").html(html);
           }
       });
    });

})();