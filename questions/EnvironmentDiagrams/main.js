let frameCount = 0;
let funcCount = 0;

function add_variable_listener(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
	//var newvar = document.createElement("div");
  if (frame.id == "globalFrame") {
    variables.appendChild(make_variable())
  } else {
    returnVal = frame.querySelector(".returnValueTr");
    variables.insertBefore(make_variable(), returnVal)
  }
}

function make_variable(plKey, returnValue=false) {
  const tr = document.createElement("tr");
  tr.classList.add("variableTr")
  var varname; 
  if (returnValue) {
    tr.classList.add("returnValueTr")
    varname = document.createElement("span")
    varname.innerText = "Return Value"
  } else {
    varname = make_variable_length_input("stackFrameVarInput", plKey + "-var")
  }
  var stackframeval = make_variable_length_input("stackFrameValueInput", plKey + "-val")

  var td = tr.insertCell();
  td.classList.add()
  if (!returnValue) {
    td.appendChild(make_remove_button(tr));
  }
  var td = tr.insertCell();
  td.classList.add("stackFrameVar")
  td.appendChild(varname);
  var td = tr.insertCell();
  td.classList.add("stackFrameValue")
	td.appendChild(stackframeval);
  return tr;
}

function make_remove_button(target) {
  var removeframe = document.createElement("button");
  removeframe.className = "removeButton"
  removeframe.onclick = function() {
    target.parentElement.removeChild(target);
  }
  return removeframe
}

function make_parent_marker(elemType, plKey) {
  var frame_parent_input = make_variable_length_input("frameParentHeader", plKey + "parent")
  marker = document.createElement(elemType)
  marker.innerHTML = " [Parent = ";
  marker.type = "text";
  marker.appendChild(frame_parent_input);
  marker.innerHTML += "]";
  return marker
}

function make_variable_length_input(className, plKey) {
  let input = document.createElement("input")
  input.classList.add(className, "pl-html-input")
  input.setAttribute("pl-html-key", plKey)
  input.addEventListener("keydown", function () {
    input.style.width = (input.value.length + 1) + "ch"
  });
  return input
}

function add_frame() {
	var frame = document.createElement("div");
  var removeframe = document.createElement("button");
  var frame_name_label = document.createElement("label");
  var frame_parent_label = document.createElement("label");
  var frame_name = make_variable_length_input("frameHeader", "f" + frameCount + "-name")
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var test = document.createElement("div");
  
  frame.className = "stackFrame";
  frame_name_label.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "stackFrameVarTable";

  removeframe = make_remove_button(frame);
  
  variable_button.innerHTML = "add variable";
  variable_button.onclick = add_variable_listener

  if (frameCount == 0) {
      frame_name_label.innerHTML = "Global frame";
      frame.id = "globalFrame"
  } else {
      frame_name_label.innerHTML = "f" + frameCount + ": ";
      frame_name_label.inner
      variables.appendChild(make_variable(true))
  }
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  if (frameCount > 0) {
    frame.appendChild(make_parent_marker("label", "f" + frameCount));
  }
  frame.appendChild(variables);
  frame.appendChild(variable_button);

  frameCount++;
  document.getElementById("globals_area").appendChild(frame);
  return frame
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
  document.getElementById("heap").appendChild(heapRow);
}

function add_function_object() {
  let funcObj = document.createElement("div")
  funcObj.className = "funcObj"
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "func" + funcCount + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"), "func" + funcCount)
  add_heap_object(funcObj)
  funcCount++;
}

let globalFrame = add_frame()
document.querySelector("#addFrameButton").addEventListener("click", add_frame)
document.querySelector("#addFuncButton").addEventListener("click", add_function_object)