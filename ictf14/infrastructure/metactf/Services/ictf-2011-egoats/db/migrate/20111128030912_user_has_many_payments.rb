class UserHasManyPayments < ActiveRecord::Migration
  def change
    change_table :payments do |t|
      t.references :user
    end
  end
end
