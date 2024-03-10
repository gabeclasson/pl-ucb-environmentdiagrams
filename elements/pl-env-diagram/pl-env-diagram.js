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
  const stackframeValueContainer = toggleContainer.closest(".variableTr").querySelector(".stackFrameValue");

  // clear existing dropdown for that checkbox
  const existingDropdown = stackframeValueContainer.querySelector(".dropdown-list");
  if (existingDropdown) {
    stackframeValueContainer.removeChild(existingDropdown);
  }

  stackframeValueInput.disabled = event.target.checked;
  stackframeValueInput.value = "";

  // check whether we are going from value -> object or object -> value
  if (event.target.checked) {
    const dropdown = document.createElement("select");
    dropdown.classList.add("dropdown-list");

    // want the top option to the empty (so it's not pre-selected)
    const emptyOption = document.createElement("option");
    emptyOption.text = "";
    dropdown.add(emptyOption);

    // pull in function names
    const funcNameInputs = document.querySelectorAll(".funcNameInput");
    funcNameInputs.forEach(input => {
      const option = document.createElement("option");
      option.text = input.value;
      dropdown.add(option);
    });

    // have the stackFrameValueInput reflect what change we've selected
    dropdown.addEventListener("change", function() {
      stackframeValueInput.value = this.value;
    });
    stackframeValueContainer.appendChild(dropdown);
  }
}

// dropdowns to render to associate a var with an object
function updateDropdowns() {
  // query for the dropdowns and func names
  const funcNameInputs = document.querySelectorAll(".funcNameInput");
  const dropdowns = document.querySelectorAll(".dropdown-list");

  // save selected elements
  const selectedValues = [];
  dropdowns.forEach(dropdown => {
    selectedValues.push(dropdown.value);
  });

  // clear the dropdown to re-render properly
  dropdowns.forEach(dropdown => {
    const currVal = dropdown.value;
    dropdown.innerHTML = "";
    const empty = document.createElement("option");
    empty.text = "";
    dropdown.add(empty);

    // TODO: re-select -> ensure that this persists
    if (selectedValues.includes(currVal)) {
      dropdown.value = currVal;
    }
  });

  // restore the dropdown with current function names
  funcNameInputs.forEach(input => {
    dropdowns.forEach(dropdown => {
      const option = document.createElement("option");
      option.text = input.value;
      dropdown.add(option);
    });
  });
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
  var stackframeval = make_value_box("stackFrameValueInput", plKey + "-val")

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
    updateDropdowns();
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

function make_value_box(className, plKey) {
  let container = document.createElement("div")
  container.className = "valueContainer"
  container.appendChild(make_variable_length_input(className, plKey))
  let pointerButton = document.createElement("button");
  pointerButton.className = "btn pointerButton"
  pointerButton.type = "button"
  pointerButton.innerHTML = "&rarr;"
  pointerButton.addEventListener("click", add_pointer_listener)
  container.appendChild(pointerButton)
  return container
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
function add_heap_object(id, content) {
  let heapRow = document.createElement("table")
  heapRow.className = "heapRow"
  let topLevelHeapObject = document.createElement("td")
  topLevelHeapObject.className = "topLevelHeapObject"
  topLevelHeapObject.id = id;
  heapRow.appendChild(topLevelHeapObject)
  heapRow.appendChild(make_remove_button(heapRow))
  let heapObject = document.createElement("div")
  heapObject.className = "heapObject";
  topLevelHeapObject.appendChild(heapObject)
  heapObject.appendChild(content)
  executionVisualizer.querySelector("#heap").appendChild(heapRow);
}

function add_function_object() {
  let index = getLastIndex("heap-func-")
  let funcObj = document.createElement("div")
  funcObj.classList.add("funcObj")
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"), "heap-func-" + index)

  funcNameInput.addEventListener("change", updateDropdowns);
  add_heap_object("heap-func-" + index, funcObj, "function")
}

let vizLayoutTd;

function add_pointer_listener(e) {
  let button = e.target
  let valueContainer = button.closest(".valueContainer")
  let svg_objs = make_arrow_svg()
  let svg = svg_objs[0]

  function mouseListener(mouseEvent) {
    let coords = relative_coordinates_obj_to_pointer(valueContainer, mouseEvent)
    update_arrow_svg(coords, svg_objs)
  }
  document.addEventListener("mousemove", mouseListener)
  vizLayoutTd.appendChild(svg)

  function clickListener(clickEvent) {
    console.log(clickEvent.target)
    clickEvent.stopPropagation()
    document.removeEventListener("mousemove", mouseListener)
    let targetObj = clickEvent.target.closest(".topLevelHeapObject")
    if (targetObj == null) {
      vizLayoutTd.removeChild(svg)
      return 
    } 
    update_arrow_svg(relative_coordinates_obj_to_obj(valueContainer, targetObj), svg_objs)
    let valueInput = valueContainer.children[0]
    valueInput.disabled = true
    valueInput.value = "#" + targetObj.id
  }
  document.addEventListener("click", clickListener, {
    capture: true,
    once: true
  })
}

function relative_coordinates_obj_to_pointer(obj1, mouseEvent) {
  let origin = vizLayoutTd.getBoundingClientRect()
  let pos1 = obj1.getBoundingClientRect()
  let x1 = pos1.x - origin.x + pos1.width/2
  let y1 = pos1.y - origin.y + pos1.height/2
  let x2 = mouseEvent.clientX - origin.x
  let y2 = mouseEvent.clientY - origin.y
  return [x1, y1, x2, y2]
}

function relative_coordinates_obj_to_obj(obj1, obj2) {
  let origin = vizLayoutTd.getBoundingClientRect()
  let pos1 = obj1.getBoundingClientRect()
  let pos2 = obj2.getBoundingClientRect()
  let x1 = pos1.x - origin.x + pos1.width/2
  let y1 = pos1.y - origin.y + pos1.height/2
  let x2 = pos2.x - origin.x
  let y2 = pos2.y - origin.y + pos2.height/2
  return [x1, y1, x2, y2]
}

function update_arrow_svg(coords, svg_objs) {
  let x1 = coords[0]
  let y1 = coords[1]
  let x2 = coords[2]
  let y2 = coords[3]
  let svg = svg_objs[0]
  let path = svg_objs[1]
  width = Math.abs(x2 - x1)
  height = Math.abs(y2 - y1)
  let originX = Math.min(x1, x2)
  let originY = Math.min(y1, y2)
  svg.style.height = height + "px"
  svg.style.width = width + 'px'
  svg.style.top = originY
  svg.style.left = originX
  svg.setAttribute("width", width)
  svg.setAttribute("height", height)
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
  svg.setAttribute('class', "pointerArrow")
  path.setAttribute("d", `M ${x1 - originX}, ${y1 - originY} L ${x2 - originX} ${y2 - originY}`)
}

function make_arrow_svg() {
  let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute("tabindex", -1)
  let newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svg.appendChild(newPath)
  return [svg, newPath]
}

let executionVisualizer;

window.addEventListener('load', function() {
  vizLayoutTd = document.getElementById("vizLayoutTdSecond")
  executionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  if (executionVisualizer) {
    executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", add_variable_listener))
    executionVisualizer.querySelector("#addFrameButton").addEventListener("click", add_frame)
    executionVisualizer.querySelector("#addFuncButton").addEventListener("click", add_function_object)
  }
});