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

function toggleCheckbox(event) {
  const toggleContainer = event.target.parentNode;
  toggleContainer.classList.toggle("active", event.target.checked);

  const stackframeValueInput = toggleContainer.closest(".variableTr").querySelector(".stackFrameValueInput");
  stackframeValueInput.disabled = event.target.checked;
  stackframeValueInput.value = "";
}

function make_variable(plKey, returnValue=false) {
  const tr = document.createElement("tr");
  tr.classList.add("variableTr")
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
  tr.appendChild(make_toggle_value_object(plKey));
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

function make_toggle_value_object(plKey) {
  const toggleContainer = document.createElement("label");
  
  const toggleSwitch = document.createElement("input");
  toggleSwitch.type = "checkbox";
  toggleContainer.appendChild(toggleSwitch);
  toggleSwitch.id = plKey + "-toggle";
  const leftLabel = document.createElement("label");
  leftLabel.innerText = "Value";

  const rightLabel = document.createElement("label");
  rightLabel.innerText = "Object";

  toggleSwitch.addEventListener("change", toggleCheckbox);

  const toggleContainerCell = document.createElement("td");
  toggleContainerCell.appendChild(toggleContainer);
  toggleContainerCell.appendChild(leftLabel);
  toggleContainerCell.appendChild(toggleSwitch);
  toggleContainerCell.appendChild(rightLabel);

  return toggleContainerCell;
}

function make_remove_button(target) {
  var removeframe = document.createElement("button");
  removeframe.classList.add("btn", "removeButton")
  removeframe.type = "button";
  removeframe.onclick = function() {
    target.parentElement.removeChild(target);
  }
  return removeframe
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
  
  frame.className = "stackFrame";
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
  executionVisualizer.querySelector("#heap").appendChild(heapRow);
}

function add_function_object() {
  let index = getLastIndex("func-")
  let funcObj = document.createElement("div")
  funcObj.className = "funcObj"
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "func-" + index + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"), "func-" + index)
  add_heap_object(funcObj)
}

let executionVisualizer;

window.addEventListener('load', function() {
  executionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  if (executionVisualizer) {
    executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", add_variable_listener))
    executionVisualizer.querySelector("#addFrameButton").addEventListener("click", add_frame)
    executionVisualizer.querySelector("#addFuncButton").addEventListener("click", add_function_object)
  }
});