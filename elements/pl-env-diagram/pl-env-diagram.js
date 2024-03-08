function getLastIndex(slug) {
  let index;
  let prevFrames = executionVisualizer.querySelectorAll('[id^="'+slug+'"]')
  let lastFrame = prevFrames[prevFrames.length - 1]
  if (!lastFrame) {
    index = 0 // This should never happen.
  } else {
    let str = lastFrame.id.substring(slug.length)
    let indexOfDash = str.indexOf("-");
    if (indexOfDash >= 0) {
      str = str.substring(0, indexOfDash)
    }
    index = parseInt(str) + 1
  }
  return index
}

function add_variable_listener(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
  let index = getLastIndex(frame.id + "-var-")
	//var newvar = document.createElement("div");
  if (frame.id == "frame-0") {
    variables.appendChild(make_variable(frame.id + "-var-" + index))
  } else {
    returnVal = frame.querySelector(".returnValueTr");
    variables.insertBefore(make_variable(frame.id + "-var-" + index), returnVal)
  }
}

function make_variable(plKey, returnValue=false) {
  const tr = document.createElement("tr");
  tr.classList.add("variableTr", "removable")
  tr.id = plKey
  var varname; 
  if (returnValue) {
    tr.classList.add("returnValueTr")
    varname = document.createElement("span")
    varname.innerText = "Return Value"
  } else {
    varname = make_variable_length_input("stackFrameVarInput", plKey + "-name")
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
  removeframe.classList.add("btn", "removeButton")
  removeframe.type = "button";
  removeframe.addEventListener("click", removeListener)
  return removeframe
}

function removeListener(e) {
  let button = e.target
  let target = button.closest(".removable")
  target.parentElement.removeChild(target);
}

function make_parent_marker(elemType, plKey) {
  var frame_parent_input = make_variable_length_input("frameParentHeader", plKey + "-parent")
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
  input.id = plKey
  input.name = plKey
  input.value = ""
  input.setAttribute("data-instavalue", "submittedValues." + plKey)
  input.addEventListener("keydown", function () {
    input.style.width = (input.value.length + 1) + "ch"
  });
  return input
}

function add_frame() {
  let index = getLastIndex("frame-")
	var frame = document.createElement("div");
  var frame_name_label = document.createElement("label");
  var frame_name = make_variable_length_input("frameHeader", "frame-" + index + "-name")
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var test = document.createElement("div");
  
  frame.classList.add("stackFrame", "removable");
  frame_name_label.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "stackFrameVarTable";

  let removeframe = make_remove_button(frame);
  
  variable_button.className = "btn"
  variable_button.type = "button"
  variable_button.innerHTML = "add variable";
  variable_button.onclick = add_variable_listener


  frame_name_label.innerHTML = "f" + index + ": ";
  frame_name_label.inner
  variables.appendChild(make_variable("frame-" + index + "-return", true))

  frame.id = "frame-" + index
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(make_parent_marker("label", "frame-" + index));
  frame.appendChild(variables);
  frame.appendChild(variable_button);

  executionVisualizer.querySelector("#globals_area").appendChild(frame);
  return frame
  //document.body.appendChild(frame);
}

function add_heap_object(content, typeName) {
  let heapRow = document.createElement("table")
  heapRow.classList.add("heapRow", "removable")
  let topLevelHeapObject = document.createElement("td")
  topLevelHeapObject.className = "topLevelHeapObject"
  heapRow.appendChild(topLevelHeapObject)
  heapRow.appendChild(make_remove_button(heapRow))
  let heapObject = document.createElement("div")
  heapObject.className = "heapObject";
  topLevelHeapObject.appendChild(heapObject)
  if (typeName) {
    let typeMarker = document.createElement("div")
    typeMarker.className = "typeLabel"
    typeMarker.innerText = typeName
    heapObject.append(typeMarker)
  }
  heapObject.appendChild(content)
  executionVisualizer.querySelector("#heap").appendChild(heapRow);
}

function add_function_object() {
  let index = getLastIndex("heap-func-")
  let funcObj = document.createElement("div")
  funcObj.id = "heap-func-" + index
  funcObj.classList.add("funcObj")
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"), "heap-func-" + index)
  add_heap_object(funcObj, "function")
}

function add_list_object() {
  let index = getLastIndex("heap-list-")
  let listObj = document.createElement("table")
  listObj.className = "listTbl"
  let listHeaderRow = document.createElement("tr")
  let listContentsRow = document.createElement("tr")
  listObj.appendChild(listHeaderRow)
  listObj.appendChild(listContentsRow)
  let appendButton = make_add_button(function () {
    
  })
  listObj.id = "heap-list-" + index
  add_heap_object(listObj, "list")
}

function decrement_list_header(listHeaderObj) {
  if (!listHeaderObj.lastChild) {
    return;
  }
  listHeaderObj.removeChild(listHeaderObj.lastChild)
}

function increment_list_header(listHeaderObj) {
  let lastHeader = listHeaderObj.lastChild
  if (!lastHeader) {
    listHeaderObj.appendChild(make_list_header_object(0))
  }
  let lastNum = parseInt(lastHeader.innerText)
  listHeaderObj.appendChild(make_list_header_object(lastNum + 1))
}

function make_list_header_object(number) {
  let obj = document.createElement("td")
  obj.className = "listHeader"
  obj.innerText = "" + number
  return obj
}

function make_add_button(onclick) {
  var addButton = document.createElement("button");
  addButton.classList.add("btn", "addButton")
  addButton.type = "button";
  addButton.onclick = onclick
  return removeframe
}

let executionVisualizer;

window.addEventListener('load', function() {
  executionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  if (executionVisualizer) {
    executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", add_variable_listener))
    executionVisualizer.querySelectorAll('.removeButton').forEach(x => x.addEventListener("click", removeListener))
    executionVisualizer.querySelector("#addFrameButton").addEventListener("click", add_frame)
    executionVisualizer.querySelector("#addFuncButton").addEventListener("click", add_function_object)
    executionVisualizer.querySelector("#addListButton").addEventListener("click", add_list_object)
  }
});