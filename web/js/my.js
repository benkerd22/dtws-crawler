$(document).ready(function() {
  var table = $('#myTable').DataTable( {
      fixedHeader: true,
      "search": {
          "regex": true
      },
      "lengthMenu": [ 30, 50, 100, 200 ],
      "order": [[ 1, 'desc']],
      "pageLength": 50,
      "columnDefs": [ 
          { 
              "type": "num-fmt", 
              "targets": [2] },
          { 
              "data": 0, 
              "targets":[0] 
          }
      ],
      aoColumnDefs: [
          {
              orderSequence: ["desc", "asc"],
              aTargets: ['_all']
          }
      ],
      dom: 'lfrtip',
      "ajax": "data.json",
      "rowCallback": function(row, data, index) {
          if (data[0] == "下架") {
              $(row).find('td:eq(0)').css('color', 'grey');
          }
          if (data[0] == "新！") {
              $(row).find('td:eq(0)').css('color', 'blue');
          }
          if (data[0] == "正常") {
              $(row).find('td:eq(0)').css('color', 'green');
          }

          if (data[5] != "0") {
              $(row).find('td:eq(5)').css('color', 'red')
          }

          var i;

          var list = [5, 6, 7, 14, 15, 16, 17];
          for (i in list) {
              if (data[i] == "0" || data[i] == 0) {
                  $(row).find('td:eq(' + i + ')').css('color', 'grey')
              }
          }

          for (i = 8; i < 14; i++) {
              if (data[i] == "17") {
                  $(row).find('td:eq(' + i + ')').css('color', 'blue');
              } else if (data[i] == "18") {
                  $(row).find('td:eq(' + i + ')').css('color', 'red');
              } else {
                  $(row).find('td:eq(' + i + ')').css('color', 'grey');
              }
          }
      }
  } );

  var count = true;

  $("#changeStatus").on("click", function(e) {
      var btn = document.getElementById("changeStatus");
      if (count) {
          table
              .column(0)
              .search("正常|新！", true)
              .draw();
          btn.innerText = "显示全部"
      } else {
          table
              .column(0)
              .search("", true)
              .draw();
          btn.innerText = "仅显示在售"
      }
      count = !count;
  });
} );


$('#myTable')
		.removeClass( 'display' )
		.addClass('table table-striped table-bordered table-hover table-condensed');

