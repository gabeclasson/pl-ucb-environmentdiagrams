var frameCount = 0;

function add_variable(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
	//var newvar = document.createElement("div");
  const tr = variables.insertRow();
  tr.classList.add("variableTr")
  var removevar = make_remove_button(tr);
  var varname = document.createElement("input");
  var stackframeval = document.createElement("input");

  var td = tr.insertCell();
  td.classList.add()
  td.appendChild(removevar);
  var td = tr.insertCell();
  td.classList.add("stackFrameVar")
  td.appendChild(varname);
  var td = tr.insertCell();
  td.classList.add("stackFrameValue")
	td.appendChild(stackframeval);
}

function make_remove_button(target) {
  var removeframe = document.createElement("button");
  removeframe.className = "removeButton"
  removeframe.onclick = function() {
    target.parentElement.removeChild(target);
  }
  return removeframe
}

function make_parent_marker(elemType) {
  var frame_parent_input = document.createElement("input");
  frame_parent_input.className = "frameParentHeader";
  marker = document.createElement(elemType)
  marker.innerHTML = "[Parent = ";
  marker.type = "text";
  marker.appendChild(frame_parent_input);
  marker.innerHTML += "]";
  return marker
}

function add_frame() {
	var frame = document.createElement("div");
  var removeframe = document.createElement("button");
  var frame_name_label = document.createElement("label");
  var frame_parent_label = document.createElement("label");
  var frame_name = document.createElement("input");
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var test = document.createElement("div");
  
  frame.className = "stackFrame";
  frame_name_label.className = "frameHeader";
  frame_name.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "stackFrameVarTable";

  removeframe = make_remove_button(frame);
  
  variable_button.innerHTML = "add variable";
  variable_button.onclick = add_variable

  if (frameCount === 0) {
      frame_name_label.innerHTML = "Global frame";
  } else {
      frame_name_label.innerHTML = "f" + frameCount;
      frame_name_label.inner
  }

  frame_parent_label = make_parent_marker("label")
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(frame_parent_label);
  frame.appendChild(variables);
  frame.appendChild(variable_button);

  frameCount++;
  document.getElementById("globals_area").appendChild(frame);
  //document.body.appendChild(frame);
}

let heapObjectCount = 0;
function add_heap_object(content) {
  let heapRow = document.createElement("table")
  heapRow.className = "heapRow"
  let topLevelHeapObject = document.createElement("td")
  topLevelHeapObject.className = "topLevelHeapObject"
  heapRow.appendChild(topLevelHeapObject)
  heapRow.appendChild(make_remove_button(heapRow))
  let heapObject = document.createElement("div")
  heapObject.className = "heapObject";
  topLevelHeapObject.appendChild(heapObject)
  heapObject.appendChild(content)
  document.getElementById("heap").appendChild(heapObject);
}

function add_function_object() {
  let funcObj = document.createElement("div")
  funcObj.className = "funcObj"
  funcObj.innerText = "func "
  let funcNameInput = document.createElement("input")
  funcNameInput.className = "funcNameInput"
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"))
  add_heap_object(funcObj)
}

let globalFrame = document.getElementById("globalFrame")
globalFrame.querySelector(".addVarButton").addEventListener("click", add_variable)
document.querySelector("#addFrameButton").addEventListener("click", add_frame)
document.querySelector("#addFuncButton").addEventListener("click", add_function_object)