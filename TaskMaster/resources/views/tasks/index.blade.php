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
<div class="user" id="userIcon">
    <i class='bx bxs-user-circle'></i>
</div>

<!-- Hidden modal -->
<div id="userModal" class="user-modal">
    <div class="modal-content">
        <span class="close" id="closeUserModal">&times;</span>
        <h2>Edit Profile</h2>

        <form action="{{ route('user.update') }}" method="POST">
            @csrf
            @method('PUT')

            <label for="userName">Name</label>
            <input type="text" id="userName" name="name" value="{{ Auth::user()->name }}" required>

            <label for="userEmail">Email</label>
            <input type="email" id="userEmail" name="email" value="{{ Auth::user()->email }}" required>

            <label for="userPassword">New Password (optional)</label>
            <input type="password" id="userPassword" name="password">

            <button type="submit" class="save-btn">Save Changes</button>
        </form>
    </div>
</div>

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
            <ul id="taskList">
                @foreach ($tasks as $task)
                <li class="task-item" data-id="{{ $task->id}}" data-title="{{ $task->title }}" data-description="{{ $task->description }}" data-completed="{{ $task->completed ? 'true' : 'false' }}">
                <div class="title-box">
                    <h2>{{ $task->title }}</h2>
                </div>
                <div class="task-box">
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
                        <button type="submit" class="save-btn">Save</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script>
    
        document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("taskModal");
    const taskList = document.getElementById("taskList");
    const userIcon = document.getElementById("userIcon");
    const userModal = document.getElementById("userModal");
    const closeUserModal = document.getElementById("closeUserModal");

    console.log("Script loaded");

    // Open modal
    userIcon.addEventListener("click", () => {
        userModal.style.display = "flex";
    });

    // Close modal with X
    closeUserModal.addEventListener("click", () => {
        userModal.style.display = "none";
    });

    // Close modal if clicking outside content
    window.addEventListener("click", (e) => {
        if (e.target === userModal) {
            userModal.style.display = "none";
        }
    });

    // Open modal when clicking any <li>
    taskList.addEventListener("click", (e) => {
        const taskItem = e.target.closest(".task-item");
        if (!taskItem) return;

        const id = taskItem.dataset.id;
        const title = taskItem.dataset.title;
        const description = taskItem.dataset.description || "";

        openTaskModal(id, title, description);
    });

    // Stop event bubbling from buttons
    document.querySelectorAll(".status-btn, .delete-btn").forEach(btn => {
        btn.addEventListener("click", (e) => e.stopPropagation());
    });

    function openTaskModal(id, title, description) {
        document.getElementById("modalTitle").innerText = title;
        document.getElementById("modalDescription").innerText = description || "No description yet.";
        document.getElementById("modalTextarea").value = description || "";
        document.getElementById("descriptionForm").action = `/tasks/${id}`;
        modal.style.display = "flex";
    }

    // Close modal
    window.closeTaskModal = () => (modal.style.display = "none");

    window.onclick = (event) => {
        if (event.target === modal) modal.style.display = "none";
    };

});

</script>
</body>
</html>
