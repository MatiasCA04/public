<?php

use App\Http\Controllers\TaskController;
use App\Http\Controllers\Auth\RegisterController;
use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\UserController;

Route::get('/', function () {
    return view('auth.login'); 
})->name('login');

Route::post('/login', [LoginController::class, 'login'])->name('login.submit');
Route::post('/logout', [LoginController::class, 'logout'])->name('logout');

Route::get('/register', [RegisterController::class, 'showRegisterForm'])->name('register');
Route::post('/register', [RegisterController::class, 'register']);

Route::get('/tasks', function () {
    return view('tasks.index');
});

Route::resource('tasks', TaskController::class);
Route::patch('/tasks/{task}/toggle', [TaskController::class, 'toggle'])->name('tasks.toggle');

Route::put('/user/update', [UserController::class, 'update'])->name('user.update')->middleware('auth');