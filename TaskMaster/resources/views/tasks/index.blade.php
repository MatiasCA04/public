<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Manager</title>
    {{-- Load CSS with Vite --}}
    @vite('resources/css/tasks.css')
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <link href='https://cdn.jsdelivr.net/npm/pretty-checkbox@3.0/dist/pretty-checkbox.min.css' rel='stylesheet'>
</head>
<body class="">
    <div class="wrapper">
        <form action="{{ route('tasks.store') }}" method="POST" class="mb-4">
            @csrf
            <h1>Tasks</h1>
            <div class="wrapper2">
                <div class="input-box">
                    <input type="text" name="title" placeholder="New Task" class="border p-2">
                </div>
                <button type="submit" class="btn">Add</button>
            </div>
        </form>

        <div class="wrapper3">
            <ul>
                @foreach ($tasks as $task)
                <li class="task-item" onclick="openTaskModal({{ $task->id }}, '{{ $task->title }}', '{{ $task->description }}')">
                <div class="task-box">
                    <h3>{{ $task->title }}</h3>

                {{-- Toggle Complete / Incomplete --}}
                    <form action="{{ route('tasks.toggle', $task->id) }}" method="POST" style="display:inline;">
                    @csrf
                    @method('PATCH') {{-- or @method('PUT') if your route uses PUT --}}
                        <button type="submit" class="status-btn" style="background-color: {{ $task->completed ? '#28a745' : '#ffc107' }};">
                            {{ $task->completed ? 'Not Done' : 'Done' }}
                        </button>
                    </form>

                {{-- Delete Task --}}
                    <form action="{{ route('tasks.destroy', $task->id) }}" method="POST" style="display:inline;">
                    @csrf
                    @method('DELETE')
                        <button class="delete-btn">×</button>
                    </form>
                </div>
                </li>
                @endforeach
            </ul>
            <div id="taskModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeTaskModal()">&times;</span>
                    <h2 id="modalTitle">Task Title</h2>
                    <p id="modalDescription">No description yet.</p>

                    <form id="descriptionForm" method="POST" style="margin-top:20px;">
                    @csrf
                    @method('PUT')
                        <textarea name="description" id="modalTextarea" placeholder="Add a description..." rows="4"></textarea>
                        <button type="submit" class="btn">Save</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script>
    
        document.addEventListener("DOMContentLoaded", function () {
        const addTaskBtn = document.getElementById("addTaskBtn");
        const taskInput = document.getElementById("taskInput");
        const taskList = document.getElementById("taskList"); // ul element

        addTaskBtn.addEventListener("click", function () {
            const taskTitle = taskInput.value.trim();
            if (!taskTitle) return;

            const li = document.createElement("li");
            li.innerHTML = `
                <div class="title-box">
                    <h2>${taskTitle}</h2>
                    <p class="task-description"></p>
                </div>
                <button class="btn-delete">DELETE</button>
            `;

            // Add delete functionality to the button
            li.querySelector(".btn-delete").addEventListener("click", function (e) {
                e.stopPropagation(); // prevent opening modal later
                li.remove();
            });

            taskList.appendChild(li);
            taskInput.value = "";
        });
    });

        function openTaskModal(id, title, description, completed) {
            const modal = document.getElementById("taskModal");
            document.getElementById("modalTitle").innerText = title;
            document.getElementById("modalDescription").innerText = description || "No description yet.";
            document.getElementById("modalTextarea").value = description || "";

            // Update form action dynamically
            document.getElementById("descriptionForm").action = `/tasks/${id}`;

            modal.style.display = "flex";
        }

        function closeTaskModal() {
            document.getElementById("taskModal").style.display = "none";
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById("taskModal");
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
</script>
</body>
</html>
