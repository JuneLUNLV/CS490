jQuery.fn.flexdatalist=function(e,t){"use strict";var i=function(e,t){e.each(function(){var e=$(this),i=e.data(),a=i.flexdatalist,r=i.aliascontainer;r&&(e.removeClass("flexdatalist-set").attr({style:null,tabindex:null}).val(a&&a.originalValue&&!t?a.originalValue:"").removeData("flexdatalist").removeData("aliascontainer").off(),r.remove())})};if("string"==typeof e&&"reset"!==e){if(void 0!==this[0].fvalue){var a=this[0];if("destroy"===e)i(this,t);else if("value"===e){if(void 0===t)return a.fvalue.get();a.fvalue.set(t)}else if("add"===e){if(void 0===t)return a.debug("Missing value to add!");a.fvalue.add(t)}else if("toggle"===e){if(void 0===t)return a.debug("Missing value to toggle!");a.fvalue.toggle(t)}else if("remove"===e){if(void 0===t)return a.debug("Missing value to remove!");a.fvalue.remove(t)}else if("disabled"===e){if(void 0===t)return a.fdisabled();a.fdisabled(t)}else if("string"==typeof e){if(void 0===t)return a.options.get(e);a.options.set(e,t)}return this}e={_option:t}}this.length>0&&void 0!==this[0].fvalue&&i(this);var r=$.extend({url:null,data:[],params:{},relatives:null,chainedRelatives:!1,cache:!0,cacheLifetime:60,minLength:2,groupBy:!1,selectionRequired:!1,focusFirstResult:!1,textProperty:null,valueProperty:null,visibleProperties:[],iconProperty:"thumb",searchIn:["label"],searchContain:!1,searchEqual:!1,searchByWord:!1,searchDisabled:!1,searchDelay:300,normalizeString:null,multiple:null,disabled:null,maxShownResults:100,removeOnBackspace:!0,noResultsText:'No results found for "{keyword}"',toggleSelected:!1,allowDuplicateValues:!1,redoSearchOnFocus:!0,requestType:"get",requestContentType:"x-www-form-urlencoded",resultsProperty:"results",keywordParamName:"keyword",limitOfValues:0,valuesSeparator:",",debug:!0},e);return this.each(function(e){var t=$(this),i=this,a=null,n=[],s="flex"+e,l=null,o=null;this.init=function(){var e=this.options.init();this.set.up(),l.on("focusin",function(e){i.action.redoSearchFocus(e),i.action.showAllResults(e),o&&o.addClass("focus")}).on("input keydown",function(e){9===i.keyNum(e)&&i.results.remove(),i.action.keypressValue(e,188),i.action.backSpaceKeyRemove(e)}).on("input keyup",function(e){i.action.keypressValue(e,13),i.action.keypressSearch(e),i.action.copyValue(e),i.action.backSpaceKeyRemove(e),i.action.showAllResults(e),i.action.clearValue(e),i.action.removeResults(e),i.action.inputWidth(e)}).on("focusout",function(e){o&&o.removeClass("focus"),i.action.clearText(e),i.action.clearValue(e)}),window.onresize=function(){i.position()},this.cache.gc(),e.selectionRequired&&i.fvalue.clear(!0,!0),this.fvalue._load(e.originalValue,function(){i.fdisabled(e.disabled),t.trigger("init:flexdatalist",[e])},!0)},this.action={keypressValue:function(e,t){var a=i.keyNum(e),r=l[0].value,n=i.options.get();if(r.length>0&&a===t&&!n.selectionRequired&&n.multiple){r=l[0].value;e.preventDefault(),i.fvalue.extract(r),i.results.remove()}},keypressSearch:function(e){var t=i.keyNum(e),r=l.val(),n=r.length,s=i.options.get();clearTimeout(a),(!t||13!==t&&(37>t||t>40))&&(a=setTimeout(function(){(0===s.minLength&&n>0||s.minLength>0&&n>=s.minLength)&&i.data.load(function(e){i.search.get(r,e,function(e){i.results.show(e)})})},s.searchDelay))},redoSearchFocus:function(e){var t=i.fvalue.get(),a=i.options.get(),r=l.val();a.redoSearchOnFocus&&(r.length>0&&a.multiple||r.length>0&&0===t.length)&&this.keypressSearch(e)},copyValue:function(e){if(13!==i.keyNum(e)){var t=l.val(),a=i.fvalue.get(!0),r=i.options.get();r.multiple||r.selectionRequired||t.length===a.length||i.fvalue.extract(t)}},backSpaceKeyRemove:function(e){var t=i.options.get();if(t.removeOnBackspace&&t.multiple){var a=l.val(),r=l.data("_remove");8===i.keyNum(e)&&(0===a.length?r?(i.fvalue.remove(r),l.data("_remove",null)):(console.log("remove!"),l.data("_remove",l.parents("li:eq(0)").prev())):l.data("_remove",null))}},showAllResults:function(){var e=l.val();""===(e=$.trim(e))&&0===i.options.get("minLength")&&i.data.load(function(e){i.results.show(e)})},inputWidth:function(){if(i.options.get().multiple){var e=l.val(),a=parseInt(l.css("fontSize").replace("px","")),r=t.innerWidth(),n=(e.length+1)*a;n>=40&&r>=n&&(l[0].style.width=n+"px")}},clearText:function(){var e=i.fvalue.get(),t=i.options.get();!t.multiple&&t.selectionRequired&&0===e.length&&(l[0].value="")},clearValue:function(){var e=(i.fvalue.get(),l.val()),t=i.options.get();!t.multiple&&t.selectionRequired&&e.length<=t.minLength&&i.fvalue.clear()},removeResults:function(){var e=(i.fvalue.get(),l.val()),t=i.options.get();t.minLength>0&&e.length<t.minLength&&i.results.remove()}},this.set={up:function(){l=this.alias(),i.options.get("multiple")?o=this.multipleInput(l):l.insertAfter(t),t.attr("autofocus")&&l.focus(),t.data("aliascontainer",o||l).addClass("flexdatalist flexdatalist-set").css({position:"absolute",top:-14e3,left:-14e3}).attr("tabindex",-1);var e=t.attr("id"),a=l.attr("id");$('label[for="'+e+'"]').attr("for",a),this.chained()},alias:function(){var e=t.attr("id")?t.attr("id")+"-flexdatalist":s;return $('<input type="text">').attr({class:t.attr("class"),name:t.attr("name")?"flexdatalist-"+t.attr("name"):null,id:e,placeholder:t.attr("placeholder")}).addClass("flexdatalist-alias "+e).removeClass("flexdatalist").attr("autocomplete","off")},multipleInput:function(e){return o=$('<ul tabindex="1">').addClass("flexdatalist-multiple "+s).css({"border-width":"5px","border-color":"black","border-style":"solid","background-color":t.css("background-color")}).insertAfter(t).click(function(){$(this).find("input").focus()}),$('<li class="input-container">').addClass("flexdatalist-multiple-value").append(e).appendTo(o),o},chained:function(){var e=i.options.get();if(e.relatives&&e.chainedRelatives){var t=function(){e.relatives.each(function(){var e=i.isEmpty($(this).val()),t=i.isEmpty(i.value);!e&&t||i.fvalue.clear(),i.fdisabled(e)})};e.relatives.on("change",function(){t()}),t()}}},this.fvalue={get:function(e){var t=i.value;return!i.options.get().multiple&&!this.isJSON()||e?t:this.toObj(t)},set:function(e,a){return i.fdisabled()||(a||this.clear(!0),this._load(e)),t},add:function(e){return i.options.get("multiple")&&this.set(e,!0),this},toggle:function(e){return i.fdisabled()||this.multiple.toggle(e),this},remove:function(e){if(!i.fdisabled()){e=this.toObj(e),t.trigger("before:flexdatalist.remove",[e]);var a=[];if($.isArray(e))$.each(e,function(e,t){var r=i.fvalue.multiple.remove(t);r&&a.push(r)});else{var r=this.multiple.remove(e);r&&a.push(r)}t.trigger("after:flexdatalist.remove",[e,a]).trigger("change:flexdatalist",[a,i.options.get()]).trigger("change")}return this},_load:function(e,t,a){var r=i.options.get().valueProperty,n=this.toStr(e),s=this.get(!0);return t=t||$.noop,0==n.length&&0==s.length?void t(e):(e=this.toObj(e),i.isEmpty(e)||i.isEmpty(r)||"*"===r?(t(e),void i.fvalue.extract(e,a)):(i.isObject(r)||(r=r.split(",")),void i.data.load(function(a){i.isObject(e)?$.isArray(e)||(e=[e]):e=e.split(",");for(var n=[],s=0;s<e.length;s++)for(var l=e[s],o=0;o<a.length;o++)for(var u=a[o],c=0;c<r.length;c++){var f=r[c];l=i.isDefined(l,f)?l[f]:l;i.isDefined(u,f)&&l===u[f]&&n.push(u)}n.length>0&&i.fvalue.extract(n,!0),t(e)},e)))},extract:function(e,a){var r=i.options.get(),n=[];a||t.trigger("before:flexdatalist.value",[e,r]),$.isArray(e)?$.each(e,function(e,t){n.push(i.fvalue._extract(t))}):n=i.fvalue._extract(e),a||t.trigger("after:flexdatalist.value",[n,r]).trigger("change:flexdatalist",[n,r]).trigger("change")},_extract:function(e){var t=this.text(e),a=this.value(e);if((i.value,i.options.get()).multiple){if(!i.isEmpty(a)){if(i.isDup(a))return;n.push(a),this.multiple.add(a,t)}}else this.single(a,t);return{value:a,text:t}},single:function(e,t){t&&t!==l.val()&&(l[0].value=t),i.value=e},multiple:{add:function(e,t){var a=this,r=this.li(e,t);i.options.get(),r.click(function(){a.toggle($(this))}).find(".fdl-remove").click(function(){i.fvalue.remove($(this).parent())}),this.push(e),l[0].value="",this.checkLimit()},push:function(e){var t=i.fvalue.get();e=i.fvalue.toObj(e),t.push(e),e=i.fvalue.toStr(t),i.value=e},toggle:function(e){var a=i.options.get();if(a.toggleSelected){var r=this.findLi(e);if(r){var n=r.index(),s=r.data(),l=r.hasClass("disabled")?"enable":"disable",o=i.fvalue.get(),u=[{value:s.value,text:s.text,action:l},a];if(t.trigger("before:flexdatalist.toggle",u),"enable"===l){var c=r.data("value");o.splice(n,0,c),r.removeClass("disabled")}else o.splice(n,1),r.addClass("disabled");o=i.fvalue.toStr(o),i.value=o,t.trigger("after:flexdatalist.toggle",u).trigger("change:flexdatalist",u).trigger("change")}}},remove:function(e){var t=this.findLi(e);if(t){var a=i.fvalue.get(),r=t.index(),s=t.data(),l=(i.options.get(),{value:s.value,text:s.text});return a.splice(r,1),a=i.fvalue.toStr(a),i.value=a,t.remove(),i.fvalue.multiple.checkLimit(),n.splice(r,1),l}},removeAll:function(){var e=i.fvalue.get(),a=i.options.get();t.trigger("before:flexdatalist.remove.all",[e,a]),o.find("li:not(.input-container)").remove(),i.value="",n=[],t.trigger("after:flexdatalist.remove.all",[e,a])},li:function(e,t){var a=o.find("li.input-container");return $("<li>").addClass("value"+(i.options.get("toggleSelected")?" toggle":"")).append('<span class="text">'+t+"</span>").append('<span class="fdl-remove">&times;</span>').data({text:t,value:i.fvalue.toObj(e)}).insertBefore(a)},checkLimit:function(){var e=i.options.get("limitOfValues");if(e>0){var t=o.find("li.input-container");e==n.length?t.hide():t.show()}},findLi:function(e){if(e instanceof jQuery)0===e.length&&(e=null);else{var t=e;e=null,o.find("li:not(.input-container)").each(function(){var i=$(this);return i.data("value")===t?(e=i,!1):void 0})}return e},isEmpty:function(){return this.get().length>0}},value:function(e){var t=e,a=i.options.get(),r=a.valueProperty;if(i.isObject(e))if(this.isJSON()||this.isMixed())if(delete e.name_highlight,$.isArray(r)){for(var n={},s=0;s<r.length;s++)i.isDefined(e,r[s])&&(n[r[s]]=e[r[s]]);t=this.toStr(n)}else t=this.toStr(e);else t=i.isDefined(e,r)?e[r]:i.isDefined(e,a.searchIn[0])?e[a.searchIn[0]]:null;return t},text:function(e){var t=e,a=i.options.get();return i.isObject(e)&&(t=e[a.searchIn[0]],t=i.isDefined(e,a.textProperty)?e[a.textProperty]:this.placeholders.replace(e,a.textProperty,t)),$("<div>").html(t).text()},placeholders:{replace:function(e,t,a){if(i.isObject(e)&&"string"==typeof t){var r=this.parse(t);if(!i.isEmpty(e)&&r)return $.each(r,function(a,r){i.isDefined(e,r)&&(t=t.replace(a,e[r]))}),t}return a},parse:function(e){var t=e.match(/\{.+?\}/g);if(t){var i={};return t.map(function(e){i[e]=e.slice(1,-1)}),i}return!1}},clear:function(e,a){var r=i.value,s=i.options.get();return s.multiple&&this.multiple.removeAll(),i.value="",""===r||a||t.trigger("change:flexdatalist",[{value:"",text:""},s]).trigger("change"),e&&(l[0].value=""),n=[],this},toObj:function(e){if("object"!=typeof e){var t=i.options.get();i.isEmpty(e)||!i.isDefined(e)?e=t.multiple?[]:this.isJSON()?{}:"":this.isCSV()?(e=e.toString().split(t.valuesSeparator),e=$.map(e,function(e){return $.trim(e)})):(this.isMixed()||this.isJSON())&&this.isJSON(e)?e=JSON.parse(e):"number"==typeof e&&(e=e.toString())}return e},toStr:function(e){return"string"!=typeof e&&(i.isEmpty(e)||!i.isDefined(e)?e="":"number"==typeof e?e=e.toString():this.isCSV()?e=e.join(i.options.get("valuesSeparator")):(this.isJSON()||this.isMixed())&&(e=JSON.stringify(e))),$.trim(e)},isJSON:function(e){if(void 0!==e){if(i.isObject(e))e=JSON.stringify(e);else if("string"!=typeof e)return!1;return 0===e.indexOf("{")||0===e.indexOf("[{")}var t=i.options.get().valueProperty;return i.isObject(t)||"*"===t},isMixed:function(){var e=i.options.get();return!e.selectionRequired&&"*"===e.valueProperty},isCSV:function(){return!this.isJSON()&&i.options.get("multiple")}},this.data={load:function(e,i){var a=this,r=[];t.trigger("before:flexdatalist.data"),this.url(function(i){r=r.concat(i),a.static(function(i){r=r.concat(i),a.datalist(function(i){r=r.concat(i),t.trigger("after:flexdatalist.data",[r]),e(r)})})},i)},static:function(e){var t=i.options.get();if("string"==typeof t.data){var a=t.data,r=i.cache.read(a,!0);if(r)return void e(r);this.remote({url:a,success:function(r){t.data=r,e(r),i.cache.write(a,r,t.cacheLifetime,!0)}})}else"object"!=typeof t.data&&(t.data=[]),e(t.data)},datalist:function(e){var a=t.attr("list"),r=[];i.isEmpty(a)||$("#"+a).find("option").each(function(){var e=$(this),t=e.val(),i=e.text();r.push({label:i.length>0?i:t,value:t})}),e(r)},url:function(e,t){var a=l.val(),r=i.options.get(),n=r.keywordParamName,s=i.fvalue.get(),o=this.relativesData();if(i.isEmpty(r.url))return e([]);var u={};"post"===r.requestType&&($.each(r,function(e,t){0!=e.indexOf("_")&&"data"!=e&&(u[e]=t)}),delete u.relatives);var c=i.cache.keyGen({relative:o,load:t,keyword:a,contain:r.searchContain},r.url),f=i.cache.read(c,!0);if(f)e(f);else{var d=$.extend(o,r.params,{load:t,contain:r.searchContain,selected:s,original:r.originalValue,options:u});d[n]=a,this.remote({url:r.url,data:d,success:function(t){l.val().length>=a.length&&e(t),i.cache.write(c,t,r.cacheLifetime,!0)}})}},remote:function(e){var a=this,r=i.options.get();t.hasClass("flexdatalist-loading")||(t.addClass("flexdatalist-loading"),"json"===r.requestContentType&&(e.data=JSON.stringify(e.data)),$.ajax($.extend({type:r.requestType,dataType:"json",contentType:"application/"+r.requestContentType+"; charset=UTF-8",complete:function(){t.removeClass("flexdatalist-loading")}},e,{success:function(t){t=a.extractRemoteData(t),e.success(t)}})))},extractRemoteData:function(e){var t=i.options.get(),a=i.isDefined(e,t.resultsProperty)?e[t.resultsProperty]:e;return"string"==typeof a&&0===a.indexOf("[{")&&(a=JSON.parse(a)),a&&a.options&&i.options.set($.extend({},t,a.options)),i.isObject(a)?a:[]},relativesData:function(){var e=i.options.get("relatives"),t={};return e&&(t.relatives={},e.each(function(){var e=$(this),i=e.attr("name").split("][").join("-").split("]").join("-").split("[").join("-").replace(/^\|+|\-+$/g,"");t.relatives[i]=e.val()})),t}},this.search={get:function(e,a,r){if(i.options.get().searchDisabled)n=a;else{var n=i.cache.read(e);if(!n){if(t.trigger("before:flexdatalist.search",[e,a]),!i.isEmpty(e)){n=[];for(var s=this.split(e),l=0;l<a.length;l++){var o=a[l];i.isDup(o)||(o=this.matches(o,s))&&n.push(o)}}i.cache.write(e,n,2),t.trigger("after:flexdatalist.search",[e,a,n])}}r(n)},matches:function(e,t){var a=$.extend({},e),r=[],n=i.options.get(),s=n.searchIn;if(t.length>0)for(var l=0;l<s.length;l++){var o=s[l];if(i.isDefined(e,o)&&e[o]){for(var u=e[o].toString(),c=u,f=this.split(u),d=0;d<t.length;d++){var h=t[d];this.find(h,f)&&(r.push(h),c=this.highlight(h,c))}c!==u&&(a[o+"_highlight"]=this.highlight(c))}}return!(0===r.length||n.searchByWord&&r.length<t.length-1)&&a},highlight:function(e,t){return t?t.replace(new RegExp(e,i.options.get("searchContain")?"ig":"i"),"|:|$&|::|"):(e=e.split("|:|").join('<span class="highlight">')).split("|::|").join("</span>")},find:function(e,t){for(var a=i.options.get(),r=0;r<t.length;r++){var n=t[r];if(n=this.normalizeString(n),e=this.normalizeString(e),a.searchEqual)return n==e;if(a.searchContain?n.indexOf(e)>=0:0===n.indexOf(e))return!0}return!1},split:function(e){if("string"==typeof e&&(e=[$.trim(e)]),i.options.get("searchByWord"))for(var t=0;t<e.length;t++){var a=$.trim(e[t]);if(a.indexOf(" ")>0){var r=a.split(" ");$.merge(e,r)}}return e},normalizeString:function(e){if("string"==typeof e){var t=i.options.get("normalizeString");return"function"==typeof t&&(e=t(e)),e.toUpperCase()}return e}},this.results={show:function(e){var a=this,r=i.options.get();if(this.remove(!0),e){if(0===e.length)return void this.empty(r.noResultsText);var n=this.container();r.groupBy?(e=this.group(e),Object.keys(e).forEach(function(t){var s=e[t],l=r.groupBy,o=i.results.highlight(s[0],l,t);$("<li>").addClass("group").append($("<span>").addClass("group-name").html(o)).append($("<span>").addClass("group-item-count").text(" "+s.length)).appendTo(n),a.items(s,n)})):this.items(e,n);var s=n.find("li:not(.group)");s.on("click",function(){var e=$(this).data("item");e&&(i.fvalue.extract(e),a.remove(),t.trigger("select:flexdatalist",[e,r]))}).hover(function(){s.removeClass("active"),$(this).addClass("active").trigger("active:flexdatalist.results",[$(this).data("item")])},function(){$(this).removeClass("active")}),r.focusFirstResult&&s.filter(":first").addClass("active")}},empty:function(e){if(!i.isEmpty(e)){var t=this.container(),a=l.val();e=e.split("{keyword}").join(a),$("<li>").addClass("item no-results").append(e).appendTo(t)}},items:function(e,a){var r=i.options.get("maxShownResults");t.trigger("show:flexdatalist.results",[e]);for(var n=0;n<e.length&&!(r>0&&r===n);n++)this.item(e[n]).appendTo(a);t.trigger("shown:flexdatalist.results",[e])},item:function(e){for(var t=$("<li>").data("item",e).addClass("item"),a=i.options.get(),r=a.visibleProperties,n=0;n<r.length;n++){var s=r[n];if(s.indexOf("{")>-1){var l=i.fvalue.placeholders.replace(e,s),o=i.fvalue.placeholders.parse(s);u=$("<span>").addClass("item item-"+Object.values(o).join("-")).html(l+" ").appendTo(t)}else{if(a.groupBy&&a.groupBy===s||!i.isDefined(e,s))continue;var u={};if(s===a.iconProperty)u=$("<img>").addClass("item item-"+s).attr("src",e[s]);else{var c=i.results.highlight(e,s);u=$("<span>").addClass("item item-"+s).html(c+" ")}}u.appendTo(t)}return t},container:function(){var e=t;o&&(e=o);var a=$("ul.flexdatalist-results");return 0===a.length&&(a=$("<ul>").addClass("flexdatalist-results ").appendTo("body").attr("id",l.attr("id")+"-results").css({"border-color":e.css("border-left-color"),"border-width":"1px","border-bottom-left-radius":e.css("border-bottom-left-radius"),"border-bottom-right-radius":e.css("border-bottom-right-radius")}).data({target:o||l,input:t}),i.position(l)),a},group:function(e){for(var t=[],a=i.options.get("groupBy"),r=0;r<e.length;r++){var n=e[r];if(i.isDefined(n,a)){var s=n[a];i.isDefined(t,s)||(t[s]=[]),t[s].push(n)}}return t},highlight:function(e,t,a){return i.isDefined(e,t+"_highlight")?e[t+"_highlight"]:i.isDefined(e,t)?e[t]:a},remove:function(e){var i="ul.flexdatalist-results";e&&(i="ul.flexdatalist-results li"),t.trigger("remove:flexdatalist.results"),$(i).remove(),t.trigger("removed:flexdatalist.results")}},this.cache={write:function(e,t,a,r){if(i.cache.isSupported()){e=this.keyGen(e,void 0,r);var n={value:t,timestamp:i.unixtime(),lifetime:a||!1};localStorage.setItem(e,JSON.stringify(n))}},read:function(e,t){if(i.cache.isSupported()){e=this.keyGen(e,void 0,t);var a=localStorage.getItem(e);if(a){var r=JSON.parse(a);if(!this.expired(r))return r.value;localStorage.removeItem(e)}}return null},delete:function(e,t){i.cache.isSupported()&&(e=this.keyGen(e,void 0,t),localStorage.removeItem(e))},clear:function(){if(i.cache.isSupported()){for(var e in localStorage)(e.indexOf(s)>-1||e.indexOf("global")>-1)&&localStorage.removeItem(e);localStorage.clear()}},gc:function(){if(i.cache.isSupported())for(var e in localStorage)if(e.indexOf(s)>-1||e.indexOf("global")>-1){var t=localStorage.getItem(e);t=JSON.parse(t),this.expired(t)&&localStorage.removeItem(e)}},isSupported:function(){if(i.options.get("cache"))try{return"localStorage"in window&&null!==window.localStorage}catch(e){return!1}return!1},expired:function(e){if(e.lifetime){var t=i.unixtime()-e.timestamp;return e.lifetime<=t}return!1},keyGen:function(e,t,i){"object"==typeof e&&(e=JSON.stringify(e));var a,r,n=void 0===t?2166136261:t;for(a=0,r=e.length;r>a;a++)n^=e.charCodeAt(a),n+=(n<<1)+(n<<4)+(n<<7)+(n<<8)+(n<<24);return(i?"global":s)+("0000000"+(n>>>0).toString(16)).substr(-8)}},this.options={init:function(){var e=$.extend({},r,t.data(),{multiple:null===r.multiple?t.is("[multiple]"):r.multiple,disabled:null===r.disabled?t.is("[disabled]"):r.disabled,originalValue:i.value});return this.set(e),e},get:function(e){var a=t.data("flexdatalist");return e?i.isDefined(a,e)?a[e]:null:a||{}},set:function(e,a){var r=this.get();return i.isDefined(r,e)&&i.isDefined(a)?r[e]=a:i.isObject(e)&&(r=this._normalize(e)),t.data("flexdatalist",r),t},_normalize:function(e){if(e.searchIn=i.csvToArray(e.searchIn),e.relatives=e.relatives&&$(e.relatives).length>0?$(e.relatives):null,e.textProperty=null===e.textProperty?e.searchIn[0]:e.textProperty,e.visibleProperties=i.csvToArray(e.visibleProperties,e.searchIn),"*"===e.valueProperty&&e.multiple&&!e.selectionRequired)throw new Error("Selection must be required for multiple, JSON fields!");return e}},this.position=function(){var e=$("ul.flexdatalist-results"),t=e.data("target");e.length>0&&e.css({width:t.outerWidth()+"px",top:t.offset().top+t.outerHeight()+"px",left:t.offset().left+"px"})},this.fdisabled=function(e){if(this.isDefined(e)){if(t.prop("disabled",e),l.prop("disabled",e),o){o.css("background-color",t.css("background-color"));var i=o.find("li .fdl-remove"),a=o.find("li.input-container");e?(o.addClass("disabled"),i.length>0&&a.hide(),i.hide()):(o.removeClass("disabled"),a.show(),i.show())}this.options.set("disabled",e)}return this.options.get("disabled")},this.isDup=function(e){return!this.options.get("allowDuplicateValues")&&(n.length>0&&n.indexOf(this.fvalue.value(e))>-1)},this.keyNum=function(e){return e.which||e.keyCode},this.isEmpty=function(e){return!i.isDefined(e)||(null===e||!0!==e&&(0===this.length(e)||""===$.trim(e)))},this.isObject=function(e){return e&&"object"==typeof e},this.length=function(e){return this.isObject(e)?Object.keys(e).length:"number"==typeof e||"number"==typeof e.length?e.toString().length:0},this.isDefined=function(e,t){var i=void 0!==e;return i&&void 0!==t?void 0!==e[t]:i},this.unixtime=function(e){var t=new Date;return e&&(t=new Date(e)),Math.round(t.getTime()/1e3)},this.csvToArray=function(e,t){return 0===e.length?t:"string"==typeof e?e.split(i.options.get("valuesSeparator")):e},this.debug=function(e,a){var r=i.options.get();r.debug&&(a||(a={}),e="Flexdatalist: "+e,console.warn(e),console.log($.extend({inputName:t.attr("name"),options:r},a)),console.log("--- /flexdatalist ---"))},this.init()})},jQuery(function(e){e(document).data("flexdatalist")||e(document).mouseup(function(t){var i=e(".flexdatalist-results"),a=i.data("target");a&&a.is(":focus")||i.is(t.target)||0!==i.has(t.target).length||i.remove()}).keydown(function(t){var i=e(".flexdatalist-results"),a=i.find("li"),r=a.filter(".active"),n=r.index(),s=a.length,l=t.which||t.keyCode;if(0!==s){if(27===l)return void i.remove();if(13===l)t.preventDefault(),r.click();else if(40===l||38===l){t.preventDefault(),40===l?r=s>n&&r.nextAll(".item").first().length>0?r.removeClass("active").nextAll(".item").first().addClass("active"):a.removeClass("active").filter(".item:first").addClass("active"):38===l&&(r=n>0&&r.prevAll(".item").first().length>0?r.removeClass("active").prevAll(".item").first().addClass("active"):a.removeClass("active").filter(".item:last").addClass("active")),r.trigger("active:flexdatalist.results",[r.data("item")]);var o=(0===r.prev().length?r:r.prev()).position().top;i.animate({scrollTop:o+i.scrollTop()},100)}}}).data("flexdatalist",!0),jQuery("input.flexdatalist:not(.flexdatalist-set):not(.autodiscover-disabled)").flexdatalist()}),function(e){var t=e.fn.val;e.fn.val=function(e){var i=this.length>0&&void 0!==this[0].fvalue;return void 0===e?i?this[0].fvalue.get(!0):t.call(this):i?this[0].fvalue.set(e):t.call(this,e)}}(jQuery);