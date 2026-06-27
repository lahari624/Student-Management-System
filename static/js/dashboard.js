/* ==========================================
   Student Management System
   Dashboard JavaScript
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ======================================
       Live Date & Time
    ====================================== */

    function updateClock() {

        const now = new Date();

        const dateOptions = {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        };

        const date = document.getElementById("date");
        const clock = document.getElementById("clock");

        if (date) {
            date.innerHTML = now.toLocaleDateString("en-US", dateOptions);
        }

        if (clock) {
            clock.innerHTML = now.toLocaleTimeString();
        }

    }

    updateClock();

    setInterval(updateClock, 1000);

    /* ======================================
       Register Plugin
    ====================================== */

    Chart.register(ChartDataLabels);

    /* ======================================
       Department Pie Chart
    ====================================== */

    const departmentCanvas = document.getElementById("departmentChart");

    if (departmentCanvas) {

        new Chart(departmentCanvas, {

            type: "pie",

            data: {

                labels: labels,

                datasets: [{

                    data: values,

                    backgroundColor: [

                        "#4F46E5",
                        "#10B981",
                        "#F59E0B",
                        "#EF4444",
                        "#8B5CF6",
                        "#06B6D4",
                        "#EC4899",
                        "#84CC16"

                    ],

                    borderWidth: 2,
                    borderColor: "#ffffff"

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        position: "bottom"

                    },

                    datalabels: {

                        color: "#fff",

                        formatter: function(value, context){

                            let total = context.dataset.data.reduce((a,b)=>a+b);

                            return ((value/total)*100).toFixed(1)+"%";

                        }

                    }

                }

            }

        });

    }

    /* ======================================
       Gender Chart
    ====================================== */

    const genderCanvas = document.getElementById("genderChart");

    if (genderCanvas) {

        new Chart(genderCanvas, {

            type: "bar",

            data: {

                labels: genderLabels,

                datasets: [{

                    label: "Students",

                    data: genderValues,

                    backgroundColor: [

                        "#4F46E5",
                        "#EC4899"

                    ],

                    borderRadius: 10

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

    /* ======================================
       Fee Status Chart
    ====================================== */

    const feeCanvas = document.getElementById("feeChart");

    if (feeCanvas) {

        new Chart(feeCanvas, {

            type: "doughnut",

            data: {

                labels: feeLabels,

                datasets: [{

                    data: feeValues,

                    backgroundColor: [

                        "#22C55E",
                        "#EF4444"

                    ]

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        position: "bottom"

                    },

                    datalabels: {

                        color: "#fff",

                        formatter: function(value, context){

                            let total = context.dataset.data.reduce((a,b)=>a+b);

                            return ((value/total)*100).toFixed(1)+"%";

                        }

                    }

                }

            }

        });

    }

});