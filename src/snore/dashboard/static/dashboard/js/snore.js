$(document).ready(function(){
		var local=window.location.href;
		var tda=$('#menu-category li a');
		for(i=0;i<tda.length;i++){
		var cd=tda.length
		if(local.toLowerCase()==tda[i].href.toLowerCase()){
			tda[i].parentElement.className="current-menu-item";//如果当前地址和菜单栏的某个栏目地址相等，则用到样式cur
		}
		}
	})
