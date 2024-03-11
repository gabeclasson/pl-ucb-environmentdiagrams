class Visualizer {
  constructor(executionVisualizer) {
    this.executionVisualizer = executionVisualizer;
    this.vizLayoutTd = executionVisualizer.querySelector("#vizLayoutTdSecond")
  }

  getLastIndex(slug) {
    let index;
    let prevFrames = this.executionVisualizer.querySelectorAll('[id^="'+slug+'"]')
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

  add_variable_listener(e) {
    console.log(e)
    let button = e.target
    let frame = button.closest(".stackFrame")
    let variables = frame.querySelector(".stackFrameVarTable")
    console.log(this)
    let index = this.getLastIndex(frame.id + "-var-")
    //var newvar = document.createElement("div");
    if (frame.id == "frame-0") {
      variables.appendChild(this.make_variable(frame.id + "-var-" + index))
    } else {
      let returnVal = frame.querySelector(".returnValueTr");
      variables.insertBefore(this.make_variable(frame.id + "-var-" + index), returnVal)
      this.updatePointerFrom(frame.id + "-return-val", false)
    }
  }

  make_variable(plKey, returnValue=false) {
    const tr = document.createElement("tr");
    tr.classList.add("variableTr", "removable")
    tr.id = plKey
    var varname; 
    if (returnValue) {
      tr.classList.add("returnValueTr")
      varname = document.createElement("span")
      varname.innerText = "Return Value"
    } else {
      varname = this.make_variable_length_input("stackFrameVarInput", plKey + "-name")
    }
    var stackframeval = this.make_value_box("stackFrameValueInput", plKey + "-val")
  
    var td = tr.insertCell();
    td.classList.add()
    if (!returnValue) {
      td.appendChild(this.make_remove_button(tr));
    }
    var td = tr.insertCell();
    td.classList.add("stackFrameVar")
    td.appendChild(varname);
    var td = tr.insertCell();
    td.classList.add("stackFrameValue")
    td.appendChild(stackframeval);
    return tr;
  }
  
  make_remove_button(target) {
    var removeframe = document.createElement("button");
    removeframe.classList.add("btn", "removeButton")
    removeframe.type = "button";
    removeframe.addEventListener("click", (e) => this.removeListener(e))
    return removeframe
  }
  
  removeListener(e) {
    let button = e.target
    let target = button.closest(".removable")
  
    // if (target.classList.contains("topLevelHeapObject")) {
    //   this.updatePointersTo(target.id, true)
    // } else if (target.classList.contains("stackFrame")) {
    //   for (let input of Array.from(executionVisualizer.getElementsByClassName("stackFrameValueInput"))) {
    //     this.updatePointerFrom(input.id, true)
    //   } 
    // } else if (target.classList.contains("variableTr")) {
    //   this.updatePointerFrom(target.getElementsByClassName("stackFrameValueInput")[0].id, true)
    // }
  
    target.parentElement.removeChild(target);
    this.updateAllPointers()
  }
  
  updateAllPointers(thorough) {
    for (let pointer of Array.from(this.executionVisualizer.querySelectorAll(".pointerArrow"))) {
      console.log(pointer)
      this.updatePointer(pointer, thorough)
    }
  }
  
  updatePointersTo(destinationId, remove) {
    for (let pointer of Array.from(this.executionVisualizer.querySelectorAll(".pointerTo-" + destinationId))) {
      console.log(pointer)
      if (remove) {
        this.removePointer(pointer)
      } else {
        this.updatePointer(pointer)
      }
    }
  }
  
  updatePointerFrom(originId, remove) {
    let pointer = this.executionVisualizer.querySelector("#pointer-" + originId);
    if (pointer == null) {
      return
    }
    if (remove) {
      this.removePointer(pointer)
    } else {
      this.updatePointer(pointer)
    }
  }
  
  make_parent_marker(elemType, plKey) {
    var frame_parent_input = this.make_variable_length_input("frameParentHeader", plKey + "-parent")
    let marker = document.createElement(elemType)
    marker.innerHTML = " [Parent = ";
    marker.type = "text";
    marker.appendChild(frame_parent_input);
    marker.innerHTML += "]";
    return marker
  }
  
  make_value_box(className, plKey) {
    let container = document.createElement("div")
    container.className = "valueContainer"
    container.appendChild(this.make_variable_length_input(className, plKey))
    let pointerButton = document.createElement("button");
    pointerButton.className = "btn pointerButton pointerValueButton"
    pointerButton.type = "button"
    pointerButton.addEventListener("click", (e) => this.pointerValueToggleListener(e))
    container.appendChild(pointerButton)
    return container
  }
  
  make_variable_length_input(className, plKey) {
    let input = this.makeInput(className, plKey)
    let viz = this
    input.classList.add("varLengthInput")
    input.addEventListener("keyup", (e) => this.varLengthInputListener(e));
    input.addEventListener("keydown", (e) => this.varLengthInputListener(e));
    return input
  }

  varLengthInputListener(e) {
    let input = e.target
    this.updateInputLengthToContent(input)
  }
  
  makeInput(className, plKey) {
    let input = document.createElement("input")
    input.classList.add(className, "pl-html-input")
    input.id = plKey
    input.name = plKey
    input.value = ""
    return input
  }
  
  updateInputLengthToContent(input, ignorePointers) {
    let oldWidth = window.getComputedStyle(input).width
    input.style.minWidth = (input.value.length + 1) + "ch"
    if (!ignorePointers) {
      if (window.getComputedStyle(input).width != oldWidth) {
        this.updateAllPointers()
      } 
    }
  }
  
  updateAllInputLengthsToContent() {
    for (let input of this.executionVisualizer.querySelectorAll(".varLengthInput")) {
      this.updateInputLengthToContent(input, true)
    }
  }
  
  add_frame() {
    let index = this.getLastIndex("frame-")
    var frame = document.createElement("div");
    var frame_name_label = document.createElement("label");
    var frame_name = this.make_variable_length_input("frameHeader", "frame-" + index + "-name")
    var variables = document.createElement("table");
    var variable_button = document.createElement("button");
    var test = document.createElement("div");
    
    frame.classList.add("stackFrame", "removable");
    frame_name_label.className = "frameHeader";
    
    test.className = "stackFrameValue";
    
    variables.className = "stackFrameVarTable";
  
    let removeframe = this.make_remove_button(frame);
    
    variable_button.className = "btn"
    variable_button.type = "button"
    variable_button.innerHTML = "add variable";
    variable_button.onclick = ((e) => this.add_variable_listener(e))
  
  
    frame_name_label.innerHTML = "f" + index + ": ";
    frame_name_label.inner
    variables.appendChild(this.make_variable("frame-" + index + "-return", true))
  
    frame.id = "frame-" + index
    
    //frame.appendChild(test);
    frame.appendChild(removeframe);
    frame.appendChild(frame_name_label);
    frame.appendChild(frame_name);
    frame.appendChild(this.make_parent_marker("label", "frame-" + index));
    frame.appendChild(variables);
    frame.appendChild(variable_button);
  
    this.executionVisualizer.querySelector("#globals_area").appendChild(frame);
    return frame
    //document.body.appendChild(frame);
  }
  
  add_heap_object(id, content, typeName) {
    let topLevelHeapObject = document.createElement("div")
    topLevelHeapObject.classList.add("topLevelHeapObject", "removable")
    topLevelHeapObject.id = id;
    let heapObject = document.createElement("div")
    heapObject.className = "heapObject";
    topLevelHeapObject.appendChild(heapObject)
    topLevelHeapObject.appendChild(this.make_remove_button(topLevelHeapObject))
    if (typeName) {
      let typeMarker = document.createElement("div")
      typeMarker.className = "typeLabel"
      typeMarker.innerText = typeName
      heapObject.append(typeMarker)
    }
    heapObject.appendChild(content)
    this.executionVisualizer.querySelector("#heap").appendChild(topLevelHeapObject);
  }
  
  add_function_object() {
    let index = this.getLastIndex("heap-func-")
    let funcObj = document.createElement("div")
    funcObj.classList.add("funcObj")
    funcObj.innerText = "func "
    let funcNameInput = this.make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
    funcObj.appendChild(funcNameInput)
    funcObj.appendChild(this.make_parent_marker("span", "heap-func-" + index))
  
    this.add_heap_object("heap-func-" + index, funcObj, "function")
  }
  
  pointerValueToggleListener(e) {
    let button = e.target
    if (button.classList.contains("pointerButton")) {
      this.handlePointerClick(button);
    } else {
      this.handleValueClick(button);
    }
  }
  
  handlePointerClick(button) {
    let valueContainer = button.closest(".valueContainer")
    let valueInput = valueContainer.children[0]
    let pointer = this.makePointer("pointer-" + valueInput.id)
    let svg = pointer.children[0]
    let viz = this
  
    function mouseListener(mouseEvent) {
      let coords = viz.relative_coordinates_obj_to_pointer(valueInput, mouseEvent)
      viz.update_arrow_svg(coords, pointer)
    }
    this.executionVisualizer.addEventListener("mousemove", mouseListener)
    this.vizLayoutTd.appendChild(pointer)
  
    function clickListener(clickEvent) {
      clickEvent.stopPropagation()
      viz.executionVisualizer.removeEventListener("mousemove", mouseListener)
      let targetObj = clickEvent.target.closest(".topLevelHeapObject")
      if (targetObj == null) {
        viz.vizLayoutTd.removeChild(pointer)
        return 
      } 
      pointer.classList.add( "pointerTo-" + targetObj.id)
      
      viz.updatePointer(pointer, true)
    }
    this.executionVisualizer.addEventListener("click", clickListener, {
      capture: true,
      once: true
    })
  }
  
  handleValueClick(button) {
    let valueContainer = button.closest(".valueContainer")
    let valueInput = valueContainer.children[0]
    let pointerObj = this.executionVisualizer.querySelector("#pointer-" + valueInput.id)
    this.removePointer(pointerObj)
  }
  
  relative_coordinates_obj_to_pointer(obj1, mouseEvent) {
    let origin = this.vizLayoutTd.getBoundingClientRect()
    let pos1 = obj1.getBoundingClientRect()
    let x1 = pos1.x - origin.x + pos1.width/2
    let y1 = pos1.y - origin.y + pos1.height/2
    let x2 = mouseEvent.clientX - origin.x
    let y2 = mouseEvent.clientY - origin.y
    return [x1, y1, x2, y2]
  }
  
  relative_coordinates_obj_to_obj(obj1, obj2) {
    let origin = this.vizLayoutTd.getBoundingClientRect()
    let pos1 = obj1.getBoundingClientRect()
    let pos2 = obj2.getBoundingClientRect()
    let x1 = pos1.x - origin.x + pos1.width/2
    let y1 = pos1.y - origin.y + pos1.height/2
    let x2 = pos2.x - origin.x
    let y2 = pos2.y - origin.y + pos2.height/2
    return [x1, y1, x2, y2]
  }
  
  update_arrow_svg(coords, pointer) {
    let x1 = coords[0]
    let y1 = coords[1]
    let x2 = coords[2]
    let y2 = coords[3]
    let svg = pointer.children[0]
    let path = svg.children[0]
    let width = Math.abs(x2 - x1)
    let height = Math.abs(y2 - y1)
    let outerContainerX = Math.min(x1, x2)
    let outerContainerY = Math.min(y1, y2)
    svg.style.top = outerContainerY
    svg.style.left = outerContainerX
    svg.setAttribute("width", width)
    svg.setAttribute("height", height)
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
    path.setAttribute("d", `M ${x1 - outerContainerX}, ${y1 - outerContainerY} L ${x2 - outerContainerX} ${y2 - outerContainerY}`)
  }
  
  updatePointer(pointer, thorough) {
    if (pointer == null) {
      return
    }
    let originId = pointer.id.substring("pointer-".length)
    let originElement = this.executionVisualizer.querySelector("#" + originId)
    let destinationId;
    for (let className of pointer.classList) {
      if (className.indexOf("pointerTo-") >= 0) {
        destinationId = className.substring("pointerTo-".length)
      }
    }
    let destinationElement = this.executionVisualizer.querySelector("#" + destinationId)
    if (originElement == null || destinationElement == null) {
      this.removePointer(pointer)
      return;
    }

    if (thorough) {
      originElement.style.visibility = "hidden"
      originElement.value = "#" + destinationElement.id
      originElement.style.width = ""
      let button = originElement.nextElementSibling
      button.classList.add("valueButton")
      button.classList.remove("pointerButton")
    }
    this.update_arrow_svg(this.relative_coordinates_obj_to_obj(originElement, destinationElement), pointer)
  }
  
  removePointer(pointer) {
    pointer.parentElement.removeChild(pointer)
    let originId = pointer.id.substring("pointer-".length)
    let valueInput = this.executionVisualizer.querySelector("#" + originId)
    if (valueInput != null) {
      valueInput.style.visibility = "visible"
      valueInput.value = ""
      valueInput.sib
      let button = valueInput.nextElementSibling
      button.classList.add("pointerButton")
      button.classList.remove("valueButton")
    }
  }
  
  makePointer(id) {
    let container = document.createElement("div")
    container.className = "pointerArrow"
    container.id = id;
    let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    let newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    svg.appendChild(newPath)
    container.appendChild(svg)
    return container
  }
  
  add_list_object() {
    let index = this.getLastIndex("heap-list-")
    let listObj = document.createElement("table")
    listObj.className = "listTbl"
    let listHeaderRow = document.createElement("tr")
    let listContentsRow = document.createElement("tr")
    listObj.appendChild(listHeaderRow)
    listObj.appendChild(listContentsRow)
    let appendButton = this.make_add_button(function () {
      
    })
    listObj.id = "heap-list-" + index
    this.add_heap_object(listObj, "list")
  }
  
  decrement_list_header(listHeaderObj) {
    if (!listHeaderObj.lastChild) {
      return;
    }
    listHeaderObj.removeChild(listHeaderObj.lastChild)
  }
  
  increment_list_header(listHeaderObj) {
    let lastHeader = listHeaderObj.lastChild
    if (!lastHeader) {
      listHeaderObj.appendChild(this.make_list_header_object(0))
    }
    let lastNum = parseInt(lastHeader.innerText)
    listHeaderObj.appendChild(this.make_list_header_object(lastNum + 1))
  }
  
  make_list_header_object(number) {
    let obj = document.createElement("td")
    obj.className = "listHeader"
    obj.innerText = "" + number
    return obj
  }
  
  make_add_button(onclick) {
    var addButton = document.createElement("button");
    addButton.classList.add("btn", "addButton")
    addButton.type = "button";
    addButton.onclick = onclick
    return removeframe
  }

  initializeStuff() {
    this.executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", (e) => this.add_variable_listener(e)))
    this.executionVisualizer.querySelectorAll('.removeButton').forEach(x => x.addEventListener("click", (e) => this.removeListener(e)))
    this.executionVisualizer.querySelectorAll('.varLengthInput').forEach(x => x.addEventListener("keydown", (e) => this.varLengthInputListener(e)))
    this.executionVisualizer.querySelectorAll('.pointerValueButton ').forEach(x => x.addEventListener("click", (e) => this.pointerValueToggleListener(e)))
    this.executionVisualizer.querySelectorAll('.varLengthInput').forEach(x => x.addEventListener("keyup", (e) => this.varLengthInputListener(e)))
    this.executionVisualizer.querySelector("#addFrameButton").addEventListener("click", (e) => this.add_frame(e))
    this.executionVisualizer.querySelector("#addFuncButton").addEventListener("click", (e) => this.add_function_object(e))
    this.executionVisualizer.querySelector("#addListButton").addEventListener("click", (e) => this.add_list_object(e))
    this.updateAllInputLengthsToContent()
    this.updateAllPointers(true)
  }

  inactiveInitializeStuff() {
    this.updateAllInputLengthsToContent()
    this.updateAllPointers(true)
  }
}

let activeExecutionVisualizer;
window.addEventListener('load', function() {
  activeExecutionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  let viz = new Visualizer(activeExecutionVisualizer)
  viz.initializeStuff()

  for (let visualizerDOM of document.querySelectorAll('.ExecutionVisualizerInactive')) {
    let inactiveViz = new Visualizer(visualizerDOM)
    inactiveViz.inactiveInitializeStuff()
  }
});