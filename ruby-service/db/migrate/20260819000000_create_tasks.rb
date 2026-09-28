class CreateTasks < ActiveRecord::Migration[8.1]
  def change
    # `do |t| ... end` is a block. Rails yields the table builder to `t`, much
    # like a Python context manager exposes a value after `as`.
    create_table :tasks do |t|
      t.string :title, null: false
      t.boolean :completed, null: false, default: false

      t.timestamps
    end
  end
end
