(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["/minichat/latests.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "\n<div class=\"minichat-content\">\n";
var t_1;
t_1 = "none";
frame.set("previousDate", t_1, true);
if(frame.topLevel) {
context.setVariable("previousDate", t_1);
}
if(frame.topLevel) {
context.addExport("previousDate", t_1);
}
output += "\n";
frame = frame.push();
var t_4 = runtime.contextOrFrameLookup(context, frame, "results");
if(t_4) {var t_3 = t_4.length;
for(var t_2=0; t_2 < t_4.length; t_2++) {
var t_5 = t_4[t_2];
frame.set("message", t_5);
frame.set("loop.index", t_2 + 1);
frame.set("loop.index0", t_2);
frame.set("loop.revindex", t_3 - t_2);
frame.set("loop.revindex0", t_3 - t_2 - 1);
frame.set("loop.first", t_2 === 0);
frame.set("loop.last", t_2 === t_3 - 1);
frame.set("loop.length", t_3);
output += "\n    ";
if(runtime.memberLookup((runtime.memberLookup((t_5),"date")),0) != runtime.contextOrFrameLookup(context, frame, "previousDate")) {
output += "\n    <div class=\"minichat-date\">\n        ";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_5),"date")),0), env.opts.autoescape);
output += "\n    </div>\n    ";
var t_6;
t_6 = runtime.memberLookup((runtime.memberLookup((t_5),"date")),0);
frame.set("previousDate", t_6, true);
if(frame.topLevel) {
context.setVariable("previousDate", t_6);
}
if(frame.topLevel) {
context.addExport("previousDate", t_6);
}
output += "\n    ";
;
}
output += "\n\n    <div class=\"minichat-message ";
if(runtime.memberLookup((runtime.memberLookup((t_5),"user")),"username") == runtime.contextOrFrameLookup(context, frame, "user")) {
output += "self-author";
;
}
else {
output += "other-author";
;
}
output += "\">\n        <a class=\"minichat-user\" href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_5),"user")),"get_absolute_url"), env.opts.autoescape);
output += "\">\n            <img src=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((t_5),"user")),"profile")),"avatar"), env.opts.autoescape);
output += "\" title=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_5),"user")),"username"), env.opts.autoescape);
output += "\" class=\"avatar verysmallavatar\"/></a>\n        <div class=\"minichat-text\">\n            <span class=\"minichat-time\">";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_5),"date")),1), env.opts.autoescape);
output += "</span>\n            ";
output += runtime.suppressValue(runtime.memberLookup((t_5),"text"), env.opts.autoescape);
output += "\n        </div>\n    </div>\n";
;
}
}
frame = frame.pop();
output += "\n</div>\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
root: root
};

})();
})();
