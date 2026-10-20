class RemotePaymentHasOnePayment < ActiveRecord::Migration
  def change
    change_table :payments do |t|
      t.references :remote_payment
    end
  end
end
