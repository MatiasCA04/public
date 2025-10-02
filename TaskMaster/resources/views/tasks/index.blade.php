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
                    <i class='bx bx-file-blank' ></i>
                </div>
                <button class="btn">Add</button>
            </div>
        </form>
    <div class="wrapper3">    
    <ul>
        @foreach ($tasks as $task)
            <li>
                <div class="title-box">
                <h2>
                    {{ $task->title }}
                </h2>
                <form action="{{ route('tasks.update', $task) }}" method="POST" class="check-box">
                    @csrf @method('PUT')
                    <div class="pretty p-default p-thick">
                        <input type="checkbox" name="completed" onChange="this.form.submit()" {{ $task->completed ? 'checked' : '' }}>
                        <div class="state">
                            <label></label>
                        </div>
                    </div>                    
                </form>
                </div>
                <form action="{{ route('tasks.destroy', $task) }}" method="POST" class="">
                    @csrf @method('DELETE')
                    <button class="btn-delete">Delete</button>
                </form>
            </li>
        @endforeach
    </ul>
    </div>
    </div>
</body>
</html>
