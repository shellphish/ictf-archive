class CreditCard < ActiveRecord::Migration
  def change
    change_table :credit_cards do |t|
      t.references :payment
    end

  end
end
