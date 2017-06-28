function myfcn(p_list) {
    var i;

    var c_out = '';
    var pr_out = '';
    var v_out = '';


    for(i = 0; i < p_list.length; i++) {
        addentry = '<div class="box done">'+'<div class="info">'+'<h5>' + 
        p_list[i].name +
        '<a href="' + p_list[i].url + '">' + 
        '<i class="fa fa-github"></i>'+ '</a>'+

        '</h5>' +
        '<p>' + p_list[i].description + '</p>' +
        '</div></div>';

        if(p_list[i].type =="Collector"){
            c_out += addentry;
        }
        else if(p_list[i].type =="Processor"){
            pr_out += addentry;
        }
        else{ // type = visualizer
            v_out += addentry;
        }
    }
    document.getElementById("col_01").innerHTML = c_out;
    document.getElementById("col_02").innerHTML = pr_out;
    document.getElementById("col_03").innerHTML = v_out;
}
