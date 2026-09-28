# Every database-backed model inherits from this common Rails base class.
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
end
