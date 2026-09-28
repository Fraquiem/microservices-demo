require "test_helper"

class TasksTest < ActionDispatch::IntegrationTest
  setup do
    @task = Task.create!(title: "Learn Ruby", completed: false)
  end

  test "lists tasks" do
    get tasks_url

    assert_response :success
    assert_equal [@task.id], response.parsed_body.pluck("id")
  end

  test "shows a task" do
    get task_url(@task)

    assert_response :success
    assert_equal "Learn Ruby", response.parsed_body["title"]
  end

  test "creates a task from a flat JSON body" do
    assert_difference("Task.count", 1) do
      post tasks_url,
           params: { title: "Compare FastAPI", completed: false },
           as: :json
    end

    assert_response :created
    assert_equal "Compare FastAPI", response.parsed_body["title"]
  end

  test "deletes a task" do
    assert_difference("Task.count", -1) do
      delete task_url(@task)
    end

    assert_response :no_content
  end

  test "returns 404 for a missing task" do
    get task_url(999_999)

    assert_response :not_found
    assert_equal "Task not found", response.parsed_body["detail"]
  end
end
