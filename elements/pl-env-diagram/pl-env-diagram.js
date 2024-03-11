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
    updatePointerFrom(frame.id + "-return-val", false)
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
  var stackframeval = make_value_box("stackFrameValueInput", plKey + "-val")

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

  // if (target.classList.contains("topLevelHeapObject")) {
  //   updatePointersTo(target.id, true)
  // } else if (target.classList.contains("stackFrame")) {
  //   for (let input of Array.from(executionVisualizer.getElementsByClassName("stackFrameValueInput"))) {
  //     updatePointerFrom(input.id, true)
  //   } 
  // } else if (target.classList.contains("variableTr")) {
  //   updatePointerFrom(target.getElementsByClassName("stackFrameValueInput")[0].id, true)
  // }

  target.parentElement.removeChild(target);
  updateAllPointers()
}

function updateAllPointers() {
  for (let pointer of Array.from(executionVisualizer.getElementsByClassName("pointerArrow"))) {
    console.log(pointer)
    updatePointer(pointer)
  }
}

function updatePointersTo(destinationId, remove) {
  for (let pointer of Array.from(executionVisualizer.getElementsByClassName("pointerTo-" + destinationId))) {
    console.log(pointer)
    if (remove) {
      removePointer(pointer)
    } else {
      updatePointer(pointer)
    }
  }
}

function updatePointerFrom(originId, remove) {
  let pointer = executionVisualizer.getElementById("pointer-" + originId);
  if (pointer == null) {
    return
  }
  if (remove) {
    removePointer(pointer)
  } else {
    updatePointer(pointer)
  }
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
  pointerButton.className = "btn pointerButton pointerValueButton"
  pointerButton.type = "button"
  pointerButton.addEventListener("click", pointerValueToggleListener)
  container.appendChild(pointerButton)
  return container
}

function make_variable_length_input(className, plKey) {
  let input = makeInput(className, plKey)
  input.addEventListener("keyup", function () {
    updateInputLengthToContent(input)
  });
  input.addEventListener("keydown", function () {
    updateInputLengthToContent(input)
  });
  return input
}

function makeInput(className, plKey) {
  let input = document.createElement("input")
  input.classList.add(className, "pl-html-input")
  input.id = plKey
  input.name = plKey
  input.value = ""
  return input
}

function updateInputLengthToContent(input) {
  let oldWidth = window.getComputedStyle(input).width
  input.style.minWidth = (input.value.length + 1) + "ch"
  if (window.getComputedStyle(input).width != oldWidth) {
    updateAllPointers()
  } 
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

function add_heap_object(id, content, typeName) {
  let topLevelHeapObject = document.createElement("div")
  topLevelHeapObject.classList.add("topLevelHeapObject", "removable")
  topLevelHeapObject.id = id;
  let heapObject = document.createElement("div")
  heapObject.className = "heapObject";
  topLevelHeapObject.appendChild(heapObject)
  topLevelHeapObject.appendChild(make_remove_button(topLevelHeapObject))
  if (typeName) {
    let typeMarker = document.createElement("div")
    typeMarker.className = "typeLabel"
    typeMarker.innerText = typeName
    heapObject.append(typeMarker)
  }
  heapObject.appendChild(content)
  executionVisualizer.querySelector("#heap").appendChild(topLevelHeapObject);
}

function add_function_object() {
  let index = getLastIndex("heap-func-")
  let funcObj = document.createElement("div")
  funcObj.classList.add("funcObj")
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span", "heap-func-" + index))

  add_heap_object("heap-func-" + index, funcObj, "function")
}

let vizLayoutTd;

function pointerValueToggleListener(e) {
  let button = e.target
  if (button.classList.contains("pointerButton")) {
    handlePointerClick(button);
  } else {
    handleValueClick(button);
  }
}

function handlePointerClick(button) {
  let valueContainer = button.closest(".valueContainer")
  let valueInput = valueContainer.children[0]
  let pointer = makePointer("pointer-" + valueInput.id)
  let svg = pointer.children[0]

  function mouseListener(mouseEvent) {
    let coords = relative_coordinates_obj_to_pointer(valueInput, mouseEvent)
    update_arrow_svg(coords, pointer)
  }
  executionVisualizer.addEventListener("mousemove", mouseListener)
  vizLayoutTd.appendChild(pointer)

  function clickListener(clickEvent) {
    clickEvent.stopPropagation()
    executionVisualizer.removeEventListener("mousemove", mouseListener)
    let targetObj = clickEvent.target.closest(".topLevelHeapObject")
    if (targetObj == null) {
      vizLayoutTd.removeChild(pointer)
      return 
    } 
    pointer.classList.add( "pointerTo-" + targetObj.id)
    valueInput.style.visibility = "hidden"
    valueInput.value = "#" + targetObj.id
    valueInput.style.width = ""
    button.classList.add("valueButton")
    button.classList.remove("pointerButton")
    updatePointer(pointer)
  }
  executionVisualizer.addEventListener("click", clickListener, {
    capture: true,
    once: true
  })
}

function handleValueClick(button) {
  let valueContainer = button.closest(".valueContainer")
  let valueInput = valueContainer.children[0]
  let pointerObj = executionVisualizer.getElementById("pointer-" + valueInput.id)
  removePointer(pointerObj)
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

function update_arrow_svg(coords, pointer) {
  let x1 = coords[0]
  let y1 = coords[1]
  let x2 = coords[2]
  let y2 = coords[3]
  let svg = pointer.children[0]
  let path = svg.children[0]
  width = Math.abs(x2 - x1)
  height = Math.abs(y2 - y1)
  let outerContainerX = Math.min(x1, x2)
  let outerContainerY = Math.min(y1, y2)
  svg.style.top = outerContainerY
  svg.style.left = outerContainerX
  svg.setAttribute("width", width)
  svg.setAttribute("height", height)
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
  path.setAttribute("d", `M ${x1 - outerContainerX}, ${y1 - outerContainerY} L ${x2 - outerContainerX} ${y2 - outerContainerY}`)
}

function updatePointer(pointer) {
  if (pointer == null) {
    return
  }
  let originId = pointer.id.substring("pointer-".length)
  let originElement = executionVisualizer.getElementById(originId)
  let destinationId;
  for (let className of pointer.classList) {
    if (className.indexOf("pointerTo-") >= 0) {
      destinationId = className.substring("pointerTo-".length)
    }
  }
  let destinationElement = executionVisualizer.getElementById(destinationId)
  if (originElement == null || destinationElement == null) {
    removePointer(pointer)
    return;
  }
  
  update_arrow_svg(relative_coordinates_obj_to_obj(originElement, destinationElement), pointer)
  let input = pointer.children[1]
  let svg = pointer.children[0]
  let path = svg.children[0]
  input.value = JSON.stringify({
    'origin': originId,
    'destination': destinationId,
    'top': svg.style.top,
    'left': svg.style.left,
    'width': svg.width.baseVal.valueAsString,
    'height': svg.height.baseVal.valueAsString,
    'path': path.getAttribute("d")
  })
}

function removePointer(pointer) {
  pointer.parentElement.removeChild(pointer)
  let originId = pointer.id.substring("pointer-".length)
  let valueInput = executionVisualizer.getElementById(originId)
  if (valueInput != null) {
    valueInput.style.visibility = "visible"
    valueInput.value = ""
    valueInput.sib
    let button = valueInput.nextElementSibling
    button.classList.add("pointerButton")
    button.classList.remove("valueButton")
  }
}

function makePointer(id) {
  let container = document.createElement("div")
  container.className = "pointerArrow"
  container.id = id;
  let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
  let newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svg.appendChild(newPath)
  container.appendChild(svg)
  let input = makeInput("pointerInput", id + "-display")
  container.appendChild(input)
  return container
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
  vizLayoutTd = document.getElementById("vizLayoutTdSecond")
  executionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  executionVisualizer.getElementById = (id) => (executionVisualizer.querySelector("#" + id))
  executionVisualizer.getElementsByClassName = (className) => (executionVisualizer.querySelectorAll("." + className))
  if (executionVisualizer) {
    executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", add_variable_listener))
    executionVisualizer.querySelectorAll('.removeButton').forEach(x => x.addEventListener("click", removeListener))
    executionVisualizer.querySelector("#addFrameButton").addEventListener("click", add_frame)
    executionVisualizer.querySelector("#addFuncButton").addEventListener("click", add_function_object)
    executionVisualizer.querySelector("#addListButton").addEventListener("click", add_list_object)
    updateAllPointers()
  }
});