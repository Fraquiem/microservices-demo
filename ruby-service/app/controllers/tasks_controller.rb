class TasksController < ApplicationController
  # `before_action` receives symbols naming methods. Rails calls `set_task`
  # before show and destroy, avoiding duplicate lookup code.
  before_action :set_task, only: %i[show destroy]

  # Rails converts an Active Record "relation" to JSON when `render json:` is
  # used. Methods are declared with `def` and closed with `end`.
  def index
    tasks = Task.order(:id)
    render json: tasks, only: task_fields
  end

  def show
    # `@task` is an instance variable. Unlike a Python `self.task`, Ruby makes
    # it available to every method called on this controller instance.
    render json: @task, only: task_fields
  end

  def create
    task = Task.new(task_params)

    # Ruby conditionals also close with `end`; parentheses are usually omitted.
    if task.save
      # `{ ... }` denotes a Hash (Python dict). Keyword-like entries such as
      # `json:` and `status:` are symbol keys in the options Hash.
      render json: task, only: task_fields, status: :created
    else
      render json: { detail: task.errors.full_messages }, status: :unprocessable_content
    end
  end

  def destroy
    # By convention, a Ruby method ending in `!` is a more forceful variant.
    # `destroy!` raises an exception if the record cannot be deleted.
    @task.destroy!
    head :no_content
  end

  private

  def set_task
    @task = Task.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { detail: "Task not found" }, status: :not_found
  end

  def task_params
    # Rails' parameter wrapper adds the `:task` key around a flat JSON body.
    # Strong parameters then require that object and explicitly allow only
    # these fields. The client payload stays identical to FastAPI's payload.
    params.require(:task).permit(:title, :completed)
  end

  def task_fields
    %i[id title completed]
  end
end
