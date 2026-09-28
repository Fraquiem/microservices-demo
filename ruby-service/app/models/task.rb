# Active Record maps this Ruby class to the `tasks` table. Rails infers the
# table name, primary key, and attributes from the database schema.
class Task < ApplicationRecord
  # `:title` is a symbol. Here it names an attribute without allocating a
  # mutable String. This validation makes an empty or missing title invalid.
  validates :title, presence: true
end
