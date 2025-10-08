<?php

namespace App\Http\Controllers;

use App\Models\Task;
use Illuminate\Http\Request;

class TaskController extends Controller
{
    public function index()
    {
        $tasks = Task::all(); 
        return view('tasks.index', compact('tasks'));
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
        ]);

        $task = new Task();
        $task->title = $validated['title'];
        $task->completed = false;
        $task->description = null; // optional
        $task->save();

        return redirect()->route('tasks.index');
    }

    public function update(Request $request, Task $task)
    {
        $task->completed = $request->has('completed') ? $request->completed : $task->completed;
        if ($request->has('description')) {
            $task->description = $request->description;
        }
        $task->save();

        return redirect()->route('tasks.index');
    }

    public function toggle(Task $task)
    {
        $task->completed = !$task->completed;
        $task->save();

        return redirect()->back();
    }

    public function destroy(Task $task)
    {
        $task->delete();
        return redirect()->route('tasks.index');
    }
}