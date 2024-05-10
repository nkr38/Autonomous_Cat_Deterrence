$( document ).ready(function() {
    getModel()
});

setInterval(updateChartData, 5000);

function getModel(){
    $.ajax({
        url: '/get_model',
        type: 'GET',
        contentType: 'application/json',
        success: function(data) {
            $("#serialNumber").val(data['serial_number']);
            $("#armedSwitch").prop("checked", data['active']);
            $("#deviceName").val(data['device_name']);
            getPastDayChartData();
        },
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
}

function getPastDayChartData(){
    $.ajax({
        url: '/get_past_day_data',
        type: 'GET',
        contentType: 'application/json',
        success: function(data) {
            formattedData = formatDateTimeHours(data['records']);
            populateChart(formattedData, true);
        },
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
}

function getPastWeekChartData(){
    $.ajax({
        url: '/get_past_week_data',
        type: 'GET',
        contentType: 'application/json',
        success: function(data) {
            formattedData = formatMonthWeekDateTime(data['records'], 7);
            populateChart(formattedData, false);
        },
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
}

function getPastMonthChartData(){
    $.ajax({
        url: '/get_past_month_data',
        type: 'GET',
        contentType: 'application/json',
        success: function(data) {
            formattedData = formatMonthWeekDateTime(data['records'], 30);
            populateChart(formattedData, false);
        },
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
}

function getDateKey(datetime) {
    var month = datetime.getMonth() + 1;
    var day = datetime.getDate();

    return(month + '-' + day);
}

function formatMonthWeekDateTime(records, days){
    const detectionCounts = {};
    let dateTimeList = [];
    const current_date = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(current_date);
        date.setDate(current_date.getDate() - i);
        detectionCounts[getDateKey(date)] = 0;
    }
    records.forEach(function(record){
        const dateTime = record[record.length - 1];
        dateTimeList.push(new Date(dateTime));
    });

    dateTimeList.forEach(function(dateTime){
        detectionCounts[getDateKey(dateTime)]++;
    });

    for(const key in detectionCounts){
        if(isNaN(detectionCounts[key])){
            delete detectionCounts[key];
        }
    }

    return detectionCounts;
}

function formatDateTimeHours(records){
    let dateTimeList = [];
    records.forEach(function(record){
        const dateTime = record[record.length - 1];
        dateTimeList.push(new Date(dateTime));
    });
    let detectionCounts = {};
    //console.log(dateTimeList.sort());
    for(let i = 0; i < 24; i++){
        let hourString = getHourString(i);
        detectionCounts[hourString] = 0;
    }
    dateTimeList.forEach(function(dateTime){
        const hour = dateTime.getHours();
        const hourString = getHourString(hour);
        detectionCounts[hourString]++;
    });

    for(const key in detectionCounts){
        if(isNaN(detectionCounts[key])){
            delete detectionCounts[key];
        }
    }

    return detectionCounts;
}

function getHourString(hour){
    let fromHour = hour % 12 || 12;
    let toHour = (hour + 1) % 24 % 12 || 12;

    let fromPeriod = hour < 12 ? 'AM' : 'PM';
    let toPeriod = (hour + 1) % 24 < 12 ? 'AM' : 'PM';

    return `${fromHour} ${fromPeriod} - ${toHour} ${toPeriod}`;
}

$("#headerDiv").click(function() {
    window.location.href = "/";
    $.ajax({
        url: '/logout',
        type: 'POST',
        contentType: 'application/json',
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
})

$("#applyFilter").click(updateChartData);

function updateChartData(){
    timePeriod = filterType.value;
    if (timePeriod == 'day'){
        getPastDayChartData();
    }
    else if (timePeriod == 'week'){
        getPastWeekChartData();
    }
    else {
        getPastMonthChartData();
    }
}

$("#armedSwitch").change(function() {
    const data = {'active_state': this.checked};
    $.ajax({
        url: '/active_state',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
});

$("#deviceName").blur(function(){
    const data = {'device_name': $("#deviceName").val()};
    $.ajax({
        url: '/set_device_name',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        error: function(xhr, status, error) {
            console.error(error);
            $('#errorMessage').text(error);
            $('#errorModal').show();
        }
    });
});


var myChart;
function populateChart(data, isDay){

    if (myChart) {
        myChart.destroy();
    }

    if (isDay){
        xText = 'Time Period'
    }
    else{
        xText = 'Date'
    }

    chartData = chartOptions(data);
    var ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xText
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Detection Count'
                    },
                    min: 0,
                    ticks: {
                        stepSize:1,
                        beginAtZero: true,
                        suggestedMin: 0
                    }
                }
            }
        }
    });
}

function chartOptions(data){
    const chartData = {
        labels: Object.keys(data),
        datasets: [{
            label: 'Cat Detection Tracking',
            data: Object.values(data),
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    }
    return chartData;
}
