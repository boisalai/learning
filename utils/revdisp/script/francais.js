if (typeof eedisplayFloatNDTh != 'undefined'){
	var old_eedisplayFloatNDTh = eedisplayFloatNDTh;
	
	eedisplayFloatNDTh = function(value,round){
		if (eeisnumber(value))
			return (value == 0 ? "―" : old_eedisplayFloatNDTh(value,round).replace(/-/g,"−"));
		else
			return value;
	}
}

if (typeof eedisplayFloatND != 'undefined'){
	var old_eedisplayFloatND = eedisplayFloatND;
	
	eedisplayFloatND = function(value,round){
		if (eeisnumber(value))
			return (value == 0 ? "―" : old_eedisplayFloatNDTh(value,round).replace(/-/g,"−"));
		else
			return value;
	}
}