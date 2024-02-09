var frameCount = 0;

function add_variable(variables) {
function add_variable(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
	//var newvar = document.createElement("div");
  const tr = variables.insertRow();
  tr.classList.add("variableTr")
  var removevar = document.createElement("button");
  var varname = document.createElement("input");
  var stackframeval = document.createElement("input");
  
  removevar.innerHTML = "x";
  removevar.onclick = function(){variables.deleteRow(tr)};

  
  /*newvar.appendChild(removevar);
  newvar.appendChild(varname);
  newvar.appendChild(stackframeval);*/
  var td = tr.insertCell();
  td.classList.add()
  td.appendChild(removevar);
  var td = tr.insertCell();
  td.classList.add("stackFrameVar")
  td.appendChild(varname);
  var td = tr.insertCell();
  td.classList.add("stackFrameValue")
	td.appendChild(stackframeval);
	//variables.appendChild();
}

function add_frame() {
	var frame = document.createElement("div");
  var removeframe = document.createElement("button");
  var frame_name_label = document.createElement("label");
  var frame_parent_label = document.createElement("label");
  var frame_parent_input = document.createElement("input");
  var frame_name = document.createElement("input");
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var variable_count = 0;
  var test = document.createElement("div");
  
  frame.className = "stackFrame";
  frame_name_label.className = "frameHeader";
  frame_parent_input.className = "frameParentHeader";
  frame_name.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "frameTable";
  removeframe.innerHTML = "x";
  removeframe.onclick = function() {
    cell.removeChild(frame);
    // Remove the frame when the button is clicked
    frame.removeChild(frame);
};  
  variable_button.innerHTML = "add variable";
  variable_button.onclick = function(){
    add_variable(variables); 
    variable_count = variable_count + 1;
    };

  if (frameCount === 0) {
      frame_name_label.innerHTML = "Global frame";
  } else {
      frame_name_label.innerHTML = "f" + frameCount;
      frame_name_label.inner
  }

  frame_parent_label.innerHTML = "[Parent = ";
  frame_parent_input.type = "text";
  frame_parent_label.appendChild(frame_parent_input);
  frame_parent_label.innerHTML += "]";
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(frame_parent_label);
  frame.appendChild(variables);
  frame.appendChild(variable_button);
  cell.appendChild(frame);

  frameCount++;
  document.getElementById("globals_area").appendChild(frame);
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
let globalFrame = document.getElementById("globalFrame")
globalFrame.querySelector(".addVarButton").addEventListener("click", add_variable)
document.querySelector("#addFrameButton").addEventListener("click", add_frame)