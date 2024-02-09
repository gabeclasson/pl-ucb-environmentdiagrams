function add_variable(variables) {
	//var newvar = document.createElement("div");
  const tr = variables.insertRow();
  var removevar = document.createElement("button");
  var varname = document.createElement("input");
  var stackframeval = document.createElement("div");
  var test = document.createElement("input");
  
  removevar.innerHTML = "x";
  removevar.onclick = function(){variables.deleteRow(tr)};
  
  test.className = "stringObj";
  test.size = 4;
  test.innerHTML = "hello";
  stackframeval.className = "stackFrameValue";
  
  /*newvar.appendChild(removevar);
  newvar.appendChild(varname);
  newvar.appendChild(stackframeval);*/
  var td = tr.insertCell();
  td.appendChild(removevar);
  var td = tr.insertCell();
  td.appendChild(varname);
  var td = tr.insertCell();
  stackframeval.appendChild(test);
	td.appendChild(stackframeval);
	//variables.appendChild();
}
function add_frame(cell, name) {
	var frame = document.createElement("div");
  var frame_name_label = document.createElement("label");
  var frame_name = document.createElement("input");
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var variable_count = 0;
  var test = document.createElement("div");
  
  frame.className = "stackFrame";
  frame_name_label.innerHTML = "frame name: ";
  frame_name_label.className = "frameHeader";
  //frame_name.innerHTML = name;
  frame_name.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "frameTable";
  
  variable_button.innerHTML = "add variable";
  variable_button.onclick = function(){
    add_variable(variables); 
    variable_count = variable_count + 1;
    };
  
  //frame.appendChild(test);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(variables);
  frame.appendChild(variable_button);
  cell.appendChild(frame);
  //document.body.appendChild(frame);
}

function load_environment_diagram() {
	var stackHeapTable = document.createElement("table");
  var object_buttons = document.createElement("div");
  var function_button = document.createElement("button");
  var list_button = document.createElement("button");
  var frame_button = document.createElement("button");
  var Frames = document.createElement("div");
  var Objects = document.createElement("div");
  
  
  Frames.className = "stackHeader";
  Frames.innerHTML = "Frames";
  frame_button.innerHTML = "add frame";
  frame_button.onclick = function(){add_frame(td1, "");};
  
  Objects.className = "stackHeader";
  Objects.innerHTML = "Objects";
  function_button.innerHTML = "add function";
  list_button.innerHTML = "add list";
  
  /*var tr = stackHeapTable.insertRow();
  var td = tr.insertCell();
  td.appendChild(Frames);
  var td = tr.insertCell();
  td.appendChild(Objects);*/
  
  var tr = stackHeapTable.insertRow();
  var td1 = tr.insertCell();
  td1.appendChild(frame_button);
  td1.appendChild(Frames);
  add_frame(td1, "global");
  var td2 = tr.insertCell();
  td2.appendChild(Objects);
  td2.appendChild(function_button);
  td2.appendChild(list_button);
  document.body.appendChild(stackHeapTable);
}