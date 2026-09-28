Rails.application.routes.draw do
  # `resources` is Rails' routing DSL. The `do ... end` above and below marks a
  # block, Ruby's equivalent of passing a function/callback in Python.
  #
  # `:tasks`, `:index`, etc. are symbols: immutable names commonly used as
  # identifiers and hash keys. `%i[...]` is a compact array of symbols.
  resources :tasks, only: %i[index show create destroy]
end
