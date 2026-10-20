class CreateCreditCards < ActiveRecord::Migration
  def change
    create_table :credit_cards do |t|
      t.string :number
      t.integer :month
      t.integer :year
      t.string :first_name
      t.string :last_name
      t.string :verification_value
      t.string :brand

      t.timestamps
    end
  end
end
