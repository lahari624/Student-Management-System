/* ==========================================
   Student Management System
   student.js
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    // Auto focus on search box
    const searchBox = document.querySelector(".search-box input");

    if (searchBox) {
        searchBox.focus();
    }

    // Delete confirmation
    const deleteButtons = document.querySelectorAll(".delete-btn");

    deleteButtons.forEach(function(button){

        button.addEventListener("click", function(event){

            const confirmDelete = confirm(
                "Are you sure you want to delete this student?"
            );

            if(!confirmDelete){
                event.preventDefault();
            }

        });

    });

    // Highlight attendance
    const rows = document.querySelectorAll("table tbody tr");

    rows.forEach(function(row){

        const attendanceCell = row.cells[9];

        if(attendanceCell){

            const attendance = parseInt(attendanceCell.innerText);

            if(attendance < 75){

                attendanceCell.style.color = "#dc2626";
                attendanceCell.style.fontWeight = "bold";

            }
            else{

                attendanceCell.style.color = "#16a34a";
                attendanceCell.style.fontWeight = "bold";

            }

        }

    });

});